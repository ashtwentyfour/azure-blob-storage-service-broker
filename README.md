# Service Broker for Azure Storage Account Blob Storage

## Overview

The Python Flask application in this repository implements the [v2.0 Service Broker API (Broker API)](http://docs.cloudfoundry.org/services/api.html)

The broker provisions 'Standard general-purpose v2' [storage accounts](https://docs.microsoft.com/en-us/azure/storage/common/storage-account-overview) on the Microsoft Azure public cloud platform. A new [blob storage container](https://docs.microsoft.com/en-us/azure/storage/blobs/storage-blobs-introduction) is created when an application is bound to a service instance (Standard v2 storage account) and the containers' [Shared Access Signature (SAS)](https://docs.microsoft.com/en-us/azure/cognitive-services/translator/document-translation/create-sas-tokens?tabs=Containers) is generated. This SAS token is added to the binding credentials

## Pre-requisites

* A Microsoft Azure [subscription](https://azure.microsoft.com/en-ca/free/)
* A new [resource group](https://docs.microsoft.com/en-us/azure/azure-resource-manager/management/overview) will have to be created:

  ```bash
  $ az group create -l canadaeast -n service-broker-group-1
  ```

* A new Azure application (service principal) with permissions to provision resources within the resource group will have to be created. Examples can be referenced in the [documentation](https://docs.microsoft.com/en-us/azure/active-directory/develop/howto-create-service-principal-portal)
* The above documentation also provides instructions on how to generate a client secret for the service principal
* The following [page](https://docs.microsoft.com/en-us/azure/role-based-access-control/rbac-and-directory-admin-roles#azure-roles) summarizes Azure roled and Azure RBAC, and can be used to grant a 'Contributor' role to the service principal
* Access to a [Kubernetes](https://kubernetes.io/docs/home/) cluster or a [Cloud Foundry](https://www.cloudfoundry.org/) PaaS environment will be required

## Broker App Deployment

* Build the container image:

  ```bash
  $ docker build --platform=linux/amd64 -t ashbourne1990/azure-blob-storage-service-broker:latest .
  ```

* The container deployed using this image will require the following environment variables:
    * `AZURE_TENANT_ID` (tenant ID under which the subscription was created)
    * `AZURE_REGION` (for example, `canadaeast`)
    * `AZURE_RESOURCE_GROUP`
    * `AZURE_SUBSCRIPTION_ID` 
    * `AZURE_CLIENT_ID` (client ID of the service principal created)
    * `AZURE_CLIENT_SECRET` (client secret of the service principal generated manually)
    * `SERVICE_PASSWORD` (a password which will be used to authenticate against the broker)
    * `AZURE_AUTHORITY_HOST` (login.microsoftonline.com)

* An example of the [deployment](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/) manifest which can be used to deploy the broker as a Kubernetes application (Pod) is available at `manifests/deployment-sample.yaml`
* The broker can also be deployed as a standalone containerized application:

  ```bash
  $ docker run --name service-broker -d -p 80:80 -e AZURE_RESOURCE_GROUP=service-broker-group -e AZURE_SUBSCRIPTION_ID=xxxxxxxx-d270-46bc-a389-9327765b6a7a -e AZURE_REGION=canadaeast -e AZURE_TENANT_ID=xxxxxxxx-5865-40a7-811f-2b82c8fec571 -e AZURE_CLIENT_ID=xxxxxxxx-2754-44df-8918-4762151dcb79 -e AZURE_CLIENT_SECRET=XXXX -e SERVICE_PASSWORD=XXXX -e AZURE_AUTHORITY_HOST=login.microsoftonline.com ashbourne1990/azure-blob-storage-service-broker:latest
  ```

* The following Helm chart must be deployed to Kubernetes - `https://github.com/kubernetes-retired/service-catalog/tree/master/charts/catalog` in order to enable service broker registration and service provosioning (and de-provisioning) in the cluster

## Broker Configuration

* The broker can be registered by applying the manifest - `manifests/broker-sample.yml` (the sample endpoint and username/password must be replaced with the broker application endpoint and broker credentials respectively)

  ```bash
  $ kubectl apply -f manifests/broker-sample.yml
  ```

  A new `clusterservicebroker` will be created:

  ```bash
  $ kubectl get clusterservicebroker

  NAME           URL                                                 STATUS   AGE
  azure-broker   http://admin:XXXX@storagebroker.cloud.ashcorp.com   Ready    9h
  ```

* The service plan and service class details are retrieved by Kubernetes by invoking the `/v2/catalog` GET request:

  ```bash
  $ kubectl get clusterserviceplans

  NAME                                   EXTERNAL-NAME   BROKER         CLASS                                  AGE
  c939f5a1-7ce9-4f92-99c0-a03e1d30afa3   Standard v2     azure-broker   a9968739-d9c1-4ff7-abb8-f7c965dd338d   9h
  ```

  ```bash
  $ kubectl get clusterserviceclass

  NAME                                   EXTERNAL-NAME           BROKER         AGE
  a9968739-d9c1-4ff7-abb8-f7c965dd338d   azure-storage-account   azure-broker   9h
  ```

* A new service instance can be created by processing the `manifests/serviceinstance-sample.yml` manifest (`kubectl apply -f`)
* Each service instance corresponds to a new Storage account on Azure. For example, a PUT request to `/v2/service_instances/771b94cd-73d1-4513-8062-57966c9593dd` will result in the creation of a storage account with the name 'sa771b94cd73d14513806257' 

  ```bash
  $ kubectl get serviceinstance -n default

  NAME                 CLASS                                       PLAN          STATUS   AGE
  storage-account-01   ClusterServiceClass/azure-storage-account   Standard v2   Ready    8h
  ```

* The `manifests/servicebinding-sample.yml` is an example of a service binding configuration where the secret name specified is the Kubernetes secret with the service binding information. This includes the blob container name/ID, the SAS token for the container, the storage account name/ID and the blob SAS URL:

  ```bash
  $ kubectl get servicebinding -n default

  NAME                 SERVICE-INSTANCE     SECRET-NAME    STATUS   AGE
  storage-binding-01   storage-account-01   sa-secret-01   Ready    7h42m
  ```

* The contents of the secret can be verified using:

  ```bash
  $ kubectl get secret sa-secret-01 --template={{.data.sas_token}} | base64 -d
  ```

* A binding PUT request to the endpoint `/v2/service_instances/771b94cd-73d1-4513-8062-57966c9593dd/service_bindings/31e760d1-6f4d-4de4-b0c7-574d35fc6e1a` will result in the creation of a new blob container '31e760d1-6f4d-4de4-b0c7-574d35fc6e1a' in the 'sa771b94cd73d14513806257' storage account

## Sample Application

* 