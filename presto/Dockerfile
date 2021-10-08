FROM openjdk:11 as builder

ENV MAVEN_MAJOR=3
ENV MAVEN_VERSION="${MAVEN_MAJOR}.8.3"

RUN wget --quiet https://dlcdn.apache.org/maven/maven-${MAVEN_MAJOR}/${MAVEN_VERSION}/binaries/apache-maven-${MAVEN_VERSION}-bin.tar.gz
RUN tar xfz apache-maven-${MAVEN_VERSION}-bin.tar.gz -C /opt
RUN ln -s /opt/apache-maven-${MAVEN_VERSION} /opt/maven
ENV PATH="/opt/maven/bin:${PATH}"

RUN git clone --depth 1 https://github.com/janakj/presto /presto
WORKDIR /presto

RUN mvn package -DskipTests


FROM openjdk:11

ENV PRESTO_VERSION=0.260-SNAPSHOT

COPY --from=builder /presto/presto-server/target/presto-server-${PRESTO_VERSION}/presto-server-${PRESTO_VERSION} /presto

RUN apt update \
 && apt install --yes --no-install-recommends python

WORKDIR /presto
COPY etc/config.properties ./etc/config.properties
COPY etc/jvm.config        ./etc/jvm.config
COPY etc/node.properties   ./etc/node.properties

CMD ["./bin/launcher", "run"]
