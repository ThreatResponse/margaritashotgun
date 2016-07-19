# Margarita Shotgun

## Installation

`pip install git+ssh://git@github.com/ThreatResponse/python-margaritashotgun-private.git@develop`

## Usage

```
usage: margaritashotgun [-h] (-c CONFIG | -s SERVER) [-P PORT] [-u USERNAME]
                        [-m MODULE] [-p PASSWORD] [-k KEY] [-f FILENAME]
                        [--repository] [--repository-url REPOSITORY_URL]
                        [-w WORKERS] [-v] [-b BUCKET | -o OUTPUT_DIR]
                        [-d LOG_DIR] [--log_prefix LOG_PREFIX]

Remote memory aquisition wrapper for LiME

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        path to config.yml
  -s SERVER, --server SERVER
                        hostname or ip of target server
  -b BUCKET, --bucket BUCKET
                        memory dump output bucket
  -o OUTPUT_DIR, --output_dir OUTPUT_DIR
                        memory dump output directory

  -P PORT, --port PORT  ssh port on remote server
  -u USERNAME, --username USERNAME
                        username for ssh connection
  -m MODULE, --module MODULE
                        path to kernel lime kernel module
  -p PASSWORD, --password PASSWORD
                        password for user or encrypted keyfile
  -k KEY, --key KEY     path to rsa key for ssh connection
  -f FILENAME, --filename FILENAME
                        memory dump filename
  --repository          enable automatic kernel module downloads
  --repository-url REPOSITORY_URL
                        repository url
  -w WORKERS, --workers WORKERS
                        number of workers to run in parallel,default: auto
                        acceptable values are(INTEGER | "auto")
  -v, --verbose         log debug messages

  -d LOG_DIR, --log_dir LOG_DIR
                        log directory
  --log_prefix LOG_PREFIX
                        log file prefix
```

## Configuration

Margarita shotgun can be configured with a YAML formatted file passed in with the -c flag.  
  
The following config file will stream memory to an s3 bucket  

    aws:
        bucket: mshotgun
    hosts:
        - addr:     52.36.191.XXX
          port:     22
          username: ec2-user
          keyfile:  access.pem
          module:   lime-4.1.19-24.31.amzn1.x86_64.ko
    workers: 1
    repository:
        enabled: True
        url: https://threatresponse-lime-modules.s3.amazonaws.com/
    logging:
        dir: 'logs/'
        prefix: <case-number>

To write to a local file exclude the aws section from the configuration file.  
  
The `workers` configuration is an optional config item with the default configuration being a single worker.  More infomation about worker configuration is detailed in in the Parallel Execution section below.  
  
Configuration examples are included in the conf directory  

## Kernel Module Repository

Modules for the following distributions are built and hosted in the s3 bucket `https://threatresponse-lime-modules.s3.amazonaws.com/`.  This repository can be enabled with the `--repository` flag or by setting the environment variable `LIME_REPOSITORY=enabled`.  

Self hosted repositories can be configured with the `--repository-url` option or by setting the environment variable `LIME_REPOSITORY_URL`

##  AWS Credentials

Credentials will be automatically loaded from the [environment](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html#cli-config-files) or [aws config file](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html#cli-environment) as documented by amazon.

## Parallel Execution

Memory can be captured in parallel however parallelism is limited by the number of workers configured.  Each worker is spawned as a new process.  

To match the number of cpu's on the host set `workers: auto`

## Logging

TODO  

## Building

`python setup.py sdist` places build artifacts in `dist/`  

Install with `pip install dist/margarita_shotgun-*.tar.gz`  

## Tests

    py.test --cov=margaritashotgun

## License

The MIT License (MIT)

Copyright (c) 2016 Joel Ferrier

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
