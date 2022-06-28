# Service Broker for Azure Storage Account Blob Storage

## Overview

The Python Flask application in this repository implements the [v2.0 Service Broker API (Broker API)](http://docs.cloudfoundry.org/services/api.html)

The broker provisions 'Standard general-purpose v2' [storage accounts](https://docs.microsoft.com/en-us/azure/storage/common/storage-account-overview) on the Microsoft Azure public cloud platform. A new [blob storage container](https://docs.microsoft.com/en-us/azure/storage/blobs/storage-blobs-introduction) is created when an application is bound to a service instance (Standard v2 storage account) and the containers' [Shared Access Signature (SAS)](https://docs.microsoft.com/en-us/azure/cognitive-services/translator/document-translation/create-sas-tokens?tabs=Containers) is generated. This SAS token is added to the binding credentials

## Pre-requisites


