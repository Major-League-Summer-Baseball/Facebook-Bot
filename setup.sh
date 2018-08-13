#!/bin/bash  

echo "========================================="
echo "  Setting up MLSB Bot with docker!"
echo "========================================="
echo "ASSUMING the MLSB platform is running locally"

if [[ -z "${PAGE_ACCESS_TOKEN}" ]]; then
  echo "PAGE_ACCESS_TOKEN environment variable not set (value is needed - see read me)"
  exit 1
fi

if [[ -z "${VERIFY_TOKEN}" ]]; then
  echo "VERIFY_TOKEN environment variable not set (value is needed - see README)"
  exit 1
fi

if [[ -z "${ADMIN}" ]]; then
  ADMIN="admin"
  echo "ADMIN environment variable not set (default=$ADMIN)"
  export ADMIN
fi

if [[ -z "${DBNAME}" ]]; then
  DBNAME="mongo"
  echo "DBNAME environment variable not set (default=$DBNAME)"
  export DBNAME
fi

if [[ -z "${DBPW}" ]]; then
  DBPW="password"
  echo "DBPW environment variable not set (default=$DBPW)"
  export DBPW
fi

if [[ -z "${DBUSER}" ]]; then
  DBUSER="user"
  echo "DBUSER environment variable not set (default=$DBUSER)"
  export DBUSER
fi

if [[ -z "${LOCAL}" ]]; then
  LOCAL="TRUE"
  echo "LOCAL environment variable not set (default=$LOCAL)"
  export LOCAL
fi

if [[ -z "${MONGODB_URI}" ]]; then
  MONGODB_URI="mongodb://mongodb:27017/rest"
  echo "MONGODB_URI environment variable not set (default=$MONGODB_URI)"
  export MONGODB_URI
fi

if [[ -z "${PASSWORD}" ]]; then
  PASSWORD="password"
  echo "PASSWORD environment variable not set (default=$PASSWORD)"
  export PASSWORD
fi

if [[ -z "${PLATFORM}" ]]; then
  PLATFORM="http://localhost:8080"
  echo "PLATFORM environment variable not set (default=$PLATFORM)"
  export PLATFORM
fi

if [[ -z "${URI}" ]]; then
  URI="mongodb://$DBUSER:$DBPW@mongodb:27017/$DBNAME"
  echo "PLATFORM environment variable not set (default=$URI)"
  export URI
fi

docker-compose build
echo "Done building"
docker-compose up -d
echo "App is up and runnning"







