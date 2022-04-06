# Docker version for a minimal Whatizit
[Whatizit](https://doi.org/10.1093/bioinformatics/btm557) is a text processing system that allows you to do textmining tasks on text. Whatizit was created by the Rebholz Research Group at [EMBL-EBI](https://www.ebi.ac.uk/). It is based on [MONQjfa](https://github.com/HaraldKi/monqjfa), a non-deterministic and deterministic dinite automata for Java.

In this repository, we provide a dockerized version focusing mainly on the automata part coming from MONQjfa, i.e., the container does not include the web-based application nor includes the dictionaries for text-mining that were available at EMBL-EBI. A sample dictionary is included for testing purposes.

If you are interested in creating a dictionary to recognize entities in a text and normalize them against a controlled vocabulary, we provide a repository that creates a dictionary for MeSH and uses it for text-mining over two corpora. The code can be also used/adapted for other vocabularies.

**Citation**
If you want to cite Whatizit, this is the main Whatizit paper we found and used
* Dietrich Rebholz-Schuhmann, Miguel Arregui, Sylvain Gaudan, Harald Kirsch, Antonio Jimeno. Text processing through Web services: calling Whatizit, Bioinformatics, Volume 24, Issue 2, 15 January 2008, Pages 296–298, https://doi.org/10.1093/bioinformatics/btm557

If you want to cite MONQjfa code repository, you can do it as
* Harald Kirsch. monqjfa --- Nondeterministic and Deterministic Finite Automata for Java (NFA, DFA). Available at https://github.com/HaraldKi/monqjfa

If you want to cite this dockerized minimal version code repo, please cite it as
* Benjamin Wolff, Leyla Jael Castro, Dietrich Rebholz-Schuhmann. Docker version for a minimal Whaizit. Available at https://github.com/zbmed-semtec/simple-whatizit-docker

## Setting up the whatizit docker-container

1. Build a docker image: 
   ```console 
   sudo docker build -t simple_whatizit .
   ```

   if that does not work, try specifying the Dockerfile
   ```
   docker build - < Dockerfile
   ```
   
   or, in Windows, also using the Dockerfile, you can use
   ```
   Get-Content Dockerfile | docker build -t simple_whatizit .
   ```

   This will create the image and will tag it as simple_whatizit

2. Run the docker image in the background, this will start the container, including the necessary steps to create an annotation sample server
   ```
   sudo docker run -d simple_whatizit
   ```

3. Execute the container

   First find out the simple_whatizit container ID and then connect it with its bash
   ```
   sudo docker container ls --all
   sudo docker exec -it <container_ID> /bin/bash
   ```

4. Navigate to the MONQ folder
   ```
   cd $MONQ
   ```

5. Start tagging! Here we include some examples
- This example will use the server xmlElem and will recognize the word "cancer" within the tags ```<plain> </plain>```
  ```
  echo "<plain>cancer</plain>" | DistFilter svr=xmlElem | head
  ```

  The annotation added around cancer looks like

  ```
  <plain><z:sample ids="SAMPLE_1">cancer</z:sample></plain>
  ```

- Similar example without the XML tags. It will not work because the server withEl only tags text inside the tags ```<plain> </plain>```
  ```
  echo cancer | DistFilter svr=xmlElem | head
  ```
  
  The processed text will look the same as the original as no annotation was addedd

- Similar example without the XML tags but this time with the server plainText
  ```
  echo cancer | DistFilter svr=plainText | head
  ```

    The annotation added around cancer looks like

  ```
  <z:sample ids="SAMPLE_1">cancer</z:sample>
  ```

- Example over a text file with the server plainText
  ```
  cat ./text/annotate.txt | DistFilter svr=plainText | head
  ```

    The annotation added around cancer looks like

  ```
  <z:sample ids="SAMPLE_1">cancer</z:sample>
  ```

Visit the folder `monq/doc` for more details and the [MONQjfa documentation](http://haraldki.github.io/monqjfa/monqApiDoc/index.html)

## Adding a new dictionary and server

For testing purposes, once you are inside the container, you can duplicate `monq/sample.mwt` and and `config/plainText.svr` to try out the creation of dictionaries and servers. Make sure you are inside the `$MONQ` folder.

Be aware that these new dictionary and server will not persist beyond the container instance that you are using at the time.

Name the "new" dictionary as `automata/myTest.mwt` and the "new" server as `config/myPlaintest.svr`. Add a new element to `automata/myTest.mwt` to recognize the test whatizit. It will look like
  ```
  <?xml version='1.0' encoding='UTF-8'?>
  <mwt xmlns:z="http://a.url/z">
  <template><z:sample ids="%1">%0</z:sample></template>

  <t p1="SAMPLE_1">cancer</t>
  <t p1="SAMPLE_2">zyx</t>
  <t p1="SAMPLE_3">AGPAT3</t>
  <t p1="SAMPLE_3">1-acyl-sn-glycerol-3-phosphate acyltransferase gamma</t>
  <t p1="SAMPLE_4">+ delta cadinene synthase isozyme C2</t>
  <t p1="SAMPLE_5">cancer</t>
  <t p1="SAMPLE_6">whatizit</t>

  <template>%0</template>
  <r><z:[^>]*>(.*</z)!:[^>]*></r>
  </mwt>
  ```

Modify `config/myPlaintest.svr` to work with this dictionary, make sure to change the host number and the port to anything that is not used in the other two servers. It could look like
   ```
  <svr>
    <synopsis>tags sample words</synopsis>
    <environment>
    </environment>
    <access>public</access>
    <host>abc12341234</host>
    <port>8028</port>
    <cmd>DictFilter -Xmx2000m -XX:MinHeapFreeRatio=10 -XX:MaxHeapFreeRatio=10 :: -t raw -p ${port} -ie UTF-8 -oe UTF-8 ${MONQ}/automata/myTest.mwt</cmd>
  </svr>
   ```

   Run the following code
   ```
  cd ${MONQ}/config && \
  hostnamevar=$(hostname) && \
  sed -i "s/<host>.*</<host>$hostnamevar</" *.svr && \
  cd ${MONQ}/bin && \
  echo y | ./startServer myPlaintest
   ```

  You should see the output `Starting myPlainTest on 8028, logfile is /home/whatizit/monq/logging/myPlainTest.log .` Wait a minute to allow the server to fully start and try `echo whatizit | DistFilter svr=myPlainTest | head`. You should get the annotation ` <z:sample ids="SAMPLE_6">whatizit</z:sample>`.


