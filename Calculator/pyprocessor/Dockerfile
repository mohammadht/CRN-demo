# Copyright 2018 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# -----------------------------------------------------------------------------

FROM ubuntu:xenial

RUN \
 apt-get update; \
 apt-get install curl -y; \
 curl -sSL 'http://keyserver.ubuntu.com/pks/lookup?op=get&search=0x8AA7AF1F1091A5FD' | apt-key add - \
 && echo "deb [arch=amd64] http://repo.sawtooth.me/ubuntu/bumper/stable xenial universe" >> /etc/apt/sources.list \
 && apt-get update \
 && apt-get install -y -q \
    apt-transport-https \
    build-essential \
    ca-certificates \
    python3-sawtooth-sdk \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

EXPOSE 4004/tcp

WORKDIR /project/calculator/pyprocessor
ENV PATH "$PATH:/project/calculator/pyprocessor"

CMD bash -c 'python3 ./calculator_tp.py'
