FROM ubuntu:22.04 as base

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y \
        autoconf2.13 \
        build-essential \
        cmake \
        curl \
        git \
        libboost-all-dev \
        libcurl4-openssl-dev \
        libgmp-dev \
        libpq-dev \
        libpqxx-dev \
        libssl-dev \
        ninja-build \
        openssl \
        python3-pkgconfig && \
    apt-get clean && \
    rm -rf /var/cache/apt/lists/*

FROM base as builder
WORKDIR /root
RUN mkdir /root/history-tools
COPY cmake /root/history-tools/cmake
COPY CMakeLists.txt /root/history-tools
COPY libraries /root/history-tools/libraries
COPY src /root/history-tools/src
COPY unittests /root/history-tools/unittests

# build openssl 1.1.1
RUN curl -kfsSLO https://www.openssl.org/source/openssl-1.1.1q.tar.gz
# verify checksum
RUN echo "d7939ce614029cdff0b6c20f0e2e5703158a489a72b2507b8bd51bf8c8fd10ca  openssl-1.1.1q.tar.gz" | sha256sum -c -
RUN tar -zxf openssl-1.1.1q.tar.gz
RUN cd openssl-1.1.1q && \
    ./config && \
    make -j$(nproca) && \
    make TESTS=-test_afalg test && \
    mv /usr/bin/openssl /usr/bin/openssl3 && \
    make install && \
    ln -s /usr/local/bin/openssl /usr/bin/openssl && \
    ldconfig && \
    ldd /usr/local/bin/openssl && \
    openssl version && \
    cd .. && \
    rm -rf openssl-1.1.1q* 

#build protobuf
ENV PROTOBUF_VERSION_SHORT 21.5
ENV PROTOBUF_VERSION 3.21.5
RUN curl -fksSLO https://github.com/protocolbuffers/protobuf/releases/download/v${PROTOBUF_VERSION_SHORT}/protobuf-cpp-${PROTOBUF_VERSION}.tar.gz && \
    tar xzvf protobuf-cpp-${PROTOBUF_VERSION}.tar.gz && \
    cd protobuf-${PROTOBUF_VERSION} && \
    cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DCMAKE_POSITION_INDEPENDENT_CODE=ON -DCMAKE_INSTALL_PREFIX=/usr/local -Dprotobuf_BUILD_TESTS=OFF && \
    cmake --build build && \
    cmake --install build && \
    cd .. && \
    rm -rf protobuf-cpp-${PROTOBUF_VERSION}.tar.gz protobuf-cpp-${PROTOBUF_VERSION} && \
    ldconfig

RUN mkdir /root/history-tools/build
WORKDIR /root/history-tools/build
RUN cmake -GNinja -DCMAKE_BUILD_TYPE=Release -DPostgreSQL_TYPE_INCLUDE_DIR=/usr/include/postgresql .. && \
    ninja && \
    ctest --output-on-failure

FROM ubuntu:22.04
RUN apt-get update && \
    apt-get install -y \
        netcat \
        openssl \
        postgresql-client && \
    apt-get clean && \
    rm -rf /var/cache/apt/lists/*

COPY --from=builder /root/history-tools/build/fill-pg /usr/local/bin/fill-pg
