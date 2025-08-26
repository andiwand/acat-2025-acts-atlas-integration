#!/usr/bin/env bash

rm webpages.tar.gz
rm -rf webpages
cp -r tarball webpages
tar -czf webpages.tar.gz webpages
rm -rf webpages
