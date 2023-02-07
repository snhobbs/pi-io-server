# io-control

- Hardware driver library
- Device control library
- Shared Functions
- Business Logic
- CLI interface
- Backend server
- Frontend interface

## Physical Description

## Board Components

+ ADC
+ DAC
+ Buttons

## Setup

Emitter Board is connected to a Raspberry Pi and mounted on a Bud AN-22. The window holes of the two enclosures are lined up.
Two pins are used for alignment and a toggle clamp holds the sensor in place. 
All the sensor connections are made over an M12 to the emitter board.
Power is supplied from a bulkhead mounted barrel connector.


## Operation
- Use an auto run supervised daemon for the emitter board control
- Webserver is also supervised
  - Restarting if socket is busy, scan through sockets?

## Requirements
- Store data for future processing

## Sections
- Webserver
  - Translate web requests into commands to the underlying process
  - Reports run status
  - Controls including stopping runs
  - Supports multiple accessors
  - Give run summary
  - Optional full report on run
  - Relys on Process Control
- Process Control
  - Main function
  - Reads and aggregates data
  - Stores to disk
  - Returns status to webserver
  - Depends on hardware abstraction
