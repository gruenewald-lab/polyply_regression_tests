#!/bin/bash
count=0
touch dextrans.itp
for graph in json_graphs/*
do
echo ${graph}
polyply gen_itp -f additional_files/dextran.martini3.ff -seqf ${graph} -o dextran_itps/dextran${count}.itp -name dex${count}
cat dextran_itps/dextran${count}.itp >> dextrans.itp
let "count = count + 1"
done
