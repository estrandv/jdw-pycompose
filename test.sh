#!/bin/bash

for i in $(ls *.py | grep -v "main.py");do echo "###### $i" && python "$i";done
