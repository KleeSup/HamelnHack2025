package opcua

import (
	"context"
	"fmt"
	"log"
	"sync"
	"time"

	"github.com/gopcua/opcua"
	"github.com/gopcua/opcua/ua"
)

const (
	timeout         = 5 * time.Second
	endpoint        = "opc.tcp://192.168.5.99:4840"
	nodeErrorCode   = "ns=4;s=|var|c500.Application.Config01000.wErrorId"
	nodeMachineName = "ns=4;s=|var|c500.Application.Config01000.sMachineName"
)

type Connector struct {
	client *opcua.Client
}

func (c *Connector) watchErrorId(wg *sync.WaitGroup, interval time.Duration,
	callback func(errorID interface{}, machineName interface{}, err error)) {
	go func() {
		ticker := time.NewTicker(interval)
		defer wg.Done()
		defer ticker.Stop()

		var lastValue interface{}
		var lastMachine interface{}

		for range ticker.C {
			code, err := c.readValue(nodeErrorCode)
			machine, err2 := c.readValue(nodeMachineName)

			// only call callback when the value has changed
			if err != nil || err2 != nil || machine != lastMachine || code != lastValue {
				callback(code, machine, err)
				lastValue = code
				lastMachine = machine
			}
		}
	}()
}

func (c *Connector) readValue(nodeID string) (interface{}, error) {
	if c.client == nil {
		return nil, fmt.Errorf("client not connected")
	}

	// node ID parsing
	id, err := ua.ParseNodeID(nodeID)
	if err != nil {
		return nil, fmt.Errorf("invalid nodeId: %w", err)
	}

	// Read Request
	req := &ua.ReadRequest{
		MaxAge: 0,
		NodesToRead: []*ua.ReadValueID{
			{
				NodeID:      id,
				AttributeID: ua.AttributeIDValue,
			},
		},
		TimestampsToReturn: ua.TimestampsToReturnBoth,
	}

	// execute read
	ctx, cancel := context.WithTimeout(context.Background(), timeout)
	defer cancel()
	resp, err := c.client.Read(ctx, req)
	if err != nil {
		return nil, fmt.Errorf("read failed: %w", err)
	}

	// extract result
	if len(resp.Results) > 0 && resp.Results[0].Value != nil {
		return resp.Results[0].Value.Value(), nil
	}

	return nil, fmt.Errorf("no value returned")
}

func (c *Connector) Start(wg *sync.WaitGroup,
	caller func(errorID interface{}, machineName interface{}, err error)) error {
	// create client
	client, err := opcua.NewClient(endpoint)
	if err != nil {
		return fmt.Errorf("error creating client: %w", err)
	}

	// context with timeout and cancel function
	ctx, cancel := context.WithTimeout(context.Background(), timeout)
	defer cancel()
	// connect
	if err := client.Connect(ctx); err != nil {
		cancel()
		return fmt.Errorf("could not connect: %w", err)
	}

	// set variables
	c.client = client

	c.watchErrorId(wg, time.Second, caller)

	log.Println("OPC UA Client connected!")
	return nil
}

func (c *Connector) Close() error {
	if c.client == nil {
		return nil
	}

	// close client
	ctx, cancel := context.WithTimeout(context.Background(), timeout)
	defer cancel()
	err := c.client.Close(ctx)
	if err != nil {
		return err
	}

	log.Println("OPC UA Client was closed!")
	return nil
}

func (c *Connector) IsOpen() bool {
	return c.client != nil && c.client.State() == opcua.Connected
}
