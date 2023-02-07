---
title: Pi IO Server Design
date: 2023-02-06
---

## Components
+ Hardware Abstraction Library.
    + Generic controller for all hardware used. Generic controller for all hardware used. Contains no application information.
    + Consists of two parts, a C++ compiled library
    + Python wrapper for the C++ library in python included
+ Function Library
    + Commonly used to store shared functionality not tied to the hardware such as storage structures and file formats
+ Logic Library
    + Written in python
    + Library of tasks and high level functions specific to the application

### Visualization & Interface
+ Command line
    + The stand alone functions from the logic library are exposed as command line tools allowing quick testing and simple composition. These are declared as entry point scripts and more can be added by installing them in the bin directory.
+ Process Wrapper
    + Controller holding each task as a subprocess allowing all tasks to be spun up at once and to be started and stopped with a common interface. Controls messages between tasks. Stores persitant state for querying by an user interface.
+ Interface to process wrapper
    + Sends and receives messages from the process wrapper
    + A web interface using a Dash dashboard is used but due to the socket interface any visualization can be used, a bluetooth controller, command line tool, or any other could be added.
