# PGbencher

This playbook intend to simplify bench process for PostgreSQL database.
We have tested it with ansible 2.8.

## Dependencies

Install ansible and some dependencies

Debian based
```
apt update && apt -y install python-pip
```

Red-Hat based
```
yum install -y epel-release && yum install -y python-pip
```

Then install latest ansible and psycopg2
```
pip install -U ansible psycopg2
```

Check ansible version
```
ansible --version
ansible 2.8.3
  config file = None
  configured module search path = [u'/root/.ansible/plugins/modules', u'/usr/share/ansible/plugins/modules']
  ansible python module location = /usr/local/lib/python2.7/dist-packages/ansible
  executable location = /usr/local/bin/ansible
  python version = 2.7.13 (default, Sep 26 2018, 18:42:22) [GCC 6.3.0 20170516]
```

## Installation and Configuration
First you will need to clone this repository.
```
git clone https://github.com/wilfriedroset/pgbencher.git && cd pgbencher
```

Copy and edit the default configuration.
```
cp defaults/main.yml config.yml
```

### Parameters
PostgreSQL related parameters:
* **pgdatabase**: name of the database to use during the bench
* **pghost**: fqdn or ip of postgresql host
* **pgport**: port of postgresql
* **pgport_ro**: read-only port of postgresql
* **pgport_rw**: read-write port of postgresql
* **pguser**: name of the user to use during bench
  * you must be a superuser or have the special CREATEDB privilege
* **pgpass**: password of the user

pgbench related parameters:
* **fillfactor**: Create the pgbench_accounts, pgbench_tellers and pgbench_branches tables with the given fillfactor. Default is 100.
* **scale_factor**: Multiply the number of rows generated by the scale factor.
* **bench_plan**: list of bench to execute.

Have a look to the official documentation for more information:
https://www.postgresql.org/docs/11/pgbench.html

A bench is defined as a dictionary with:
* **bench**: type of the bench to run, one of tpcb-like, simple-update, select-only
* **client**: number of concurrent database clients
* **jobs**: number of threads
* **transactions**: number of transactions each client runs OR duration of benchmark test in seconds
  * transactions: '--transactions 100'
  * transactions: '--time 100'
* **name** (optional): name of the bench to easily identify it in summary file
* **description** (optional): description of the bench to easily understand the purpose of the bench
* **port** (optional): database server port number, will default to pgport
* **additional_options** (optional): others pgbench options, will default to none

Example
```yaml
bench_plan:
  - {name: 'bench 100 transaction on RW port',
     description: 'Bench read-write performance',
     bench: 'tpcb-like',
     port: '{{ pgport_rw }}',
     client: '{{ client }}',
     jobs: '{{ jobs }}',
     transactions: '--transactions 100',
     additional_options: '{{ additional_options }}'}
```

## Your first bench

Once configured, you can execute the playbook
```
ansible-playbook -i <host>, ./main.yml
```
Where *host* is the fqdn from which you want to run the bench.
The playbook will generate a result file formated as yaml on the host from which
you are running the playbook.

Example:
```yaml
---
bench 100 transaction on RW port:
  description: Bench read-write performance
  result:
    latency average:
      unit: ms
      value: 13.179
    number of clients: 10
    number of threads: 2
    number of transactions actually processed: 100
    number of transactions per client: 100
    query mode: simple
    scaling factor: 1
    tps (excluding connections establishing): 760.933029
    tps (including connections establishing): 758.789821
    transaction type: <builtin:TPC-B (sort of)>

    rc: 0
    stderr:
  params:
    additional_options: --vacuum-all -n -r
    bench: tpcb-like
    client: 10
    description: Bench read-write performance
    jobs: 2
    name: bench 100 transaction on RW port
    port: '5432'
    transactions: --transactions 100

bench for 100 seconds:
  description: Bench read-write performance during a given period
  result:
    duration:
      unit: s
      value: 100
    latency average:
      unit: ms
      value: 10.599
    number of clients: 10
    number of threads: 2
    number of transactions actually processed: 9428100
    query mode: simple
    scaling factor: 1
    tps (excluding connections establishing): 943.512205
    tps (including connections establishing): 943.490068
    transaction type: <builtin:TPC-B (sort of)>

    rc: 0
    stderr:
  params:
    additional_options: --vacuum-all -n -r
    bench: tpcb-like
    client: 10
    description: Bench read-write performance during a given period
    jobs: 2
    name: bench for 100 seconds
    port: '5432'
    transactions: --time 100

bench 100 transactions on RO port:
  description: Bench read-only performance
  result:
    latency average:
      unit: ms
      value: 1.039
    number of clients: 10
    number of threads: 2
    number of transactions actually processed: 100
    number of transactions per client: 100
    query mode: simple
    scaling factor: 1
    tps (excluding connections establishing): 9843.643566
    tps (including connections establishing): 9620.750034
    transaction type: <builtin:select only>

    rc: 0
    stderr:
  params:
    additional_options: --vacuum-all -n -r
    bench: select-only
    client: 10
    description: Bench read-only performance
    jobs: 2
    name: bench 100 transactions on RO port
    port: '5432'
    transactions: --transactions 100
```

With the results of your benchs you will also have the specs of the server from
which you have run the bench. This is basically the content of *ansible_facts*.

## Local test using docker

```
docker run --rm --name some-postgres -e POSTGRES_PASSWORD=$PASS -d postgres
docker run --rm -v $PWD:/mnt -it --link some-postgres:postgres debian:stretch bash
apt update && apt -y install python-pip && pip install -q psycopg2 ansible
ansible-playbook -i localhost, /mnt/main.yml
```
