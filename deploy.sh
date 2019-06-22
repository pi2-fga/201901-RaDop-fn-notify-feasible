#!/bin/bash
#
# Purpose: Continuous deploy on production environment
#
# Author: João Pedro Sconetto <sconetto.joao@gmail.com>

curl -sSL https://cli.openfaas.com | sudo sh

faas-cli -f fn-notify-feasible.yml build

faas-cli -f fn-notify-feasible.yml push