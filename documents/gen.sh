#!/bin/bash

for i in ["forecast","strategy"]; do
	for j in ["btc","eth","ltc"]; do
		for k in ["short","mid","long"] do
			touch "$i_$j_$k.html";
