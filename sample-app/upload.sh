tr -dc "A-Za-z 0-9" < /dev/urandom | fold -w100|head -n 100000 > /files/bigfile.txt

curl -H "x-ms-blob-type: BlockBlob" --upload-file /files/bigfile.txt --url "https://$ACCOUNT.blob.core.windows.net/$CONTAINER/bigfile.txt?$SAS_TOKEN"