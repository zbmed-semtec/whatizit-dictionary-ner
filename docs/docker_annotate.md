# Whatizit Docker Setup for Annotation

This script helps you set up the Whatizit container and annotate text using Docker. Please make sure you have Docker installed before running the script.


If Docker is not installed on your system, you can use the following commands to install it:

**For Linux:**

```
sudo apt update
sudo apt install docker.io
```
**For Windows:**

Follow the instructions on the Docker Desktop website.

#### 1. Build a docker image:

If you are inside the resources folder, run the following command. 

``` sudo docker build -t whatizit .```

if that does not work, try specifying the Dockerfile

``` docker build - < Dockerfile```

or, in Windows, also using the Dockerfile, you can use

``` Get-Content Dockerfile | docker build -t whatizit . ```

This will create the image and will tag it as whatizit

#### 2. Run the docker image in the background, this will start the container, including the necessary steps to create an annotation server

Without using a Docker Volume

``` sudo docker run -d whatizit ```

Starting a container with a volume

``` sudo docker run -v whatizit_volume:/data -d whatizit ```

This will create and mount a volume named 'whatizit_volume' if it does not exist into the ```/data``` directory of the 'whatizit' container

#### 3. Verify the creation of the volume.

To verify if the volume was created and mounted to the container correctly, run the following command

``` sudo docker inspect whatizit_volume ```

This should result in:

```
"Mounts": [
    {
        "Type": "volume",
        "Name": "whatizit_volume",
        "Source": "/var/lib/docker/volumes/whatizit_volume/_data",
        "Destination": "/data",
        "Driver": "local",
        "Mode": "",
        "RW": true,
        "Propagation": ""
    }
],
```

#### 4. Execute the container

First find out the whatizit container ID and then connect it with its bash

``` sudo docker container ls --all ```

``` sudo docker exec -it <container_ID> /bin/bash```


#### 5. Navigate to the MONQ folder

``` cd $MONQ ```

#### 6. Run the [Python script](../code/annotation/annotate.py) to annotate the XML files.

``` python3 annotate.py --dataset relish --n 10000```

This command takes two parameters:

+ -d/ --dataset : Name of the dataset to be annotated. (TREC/RELISH)
+ -n / --number : Number of files to annotate from the dataset.

#### 7. Output

In case of annotating trec XML files, the output will be stored in the directory ```monq/output/trec/formatted_output ```

#### 8. Copy files to your local system

To copy files in your local system, find out the container ID and execute

``` sudo docker cp <container_ID>:/data/output ~/Desktop/whatizit ```

The first path is the path in the Docker container ```/data``` and the second path is the path on your local system ```~/Desktop/whatizit```

#### 9. Create another container and mount the existing volume

To create another Docker container and use the existing volume run:

```sudo docker run -v <volume name>:/<directory on the new container> <container_name>```

To mount the volume 'whatizit_volume' at the directory ```/data``` on the new container named 'whatizit2', the command would look like this:

``` sudo docker run -v whatizit_volume:/data whatizit2 ```
