#!/bin/sh

# Copyright (c) 2018-2024, Shigemi ISHIDA
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of the Institute nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE INSTITUTE AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE INSTITUTE OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
# 

LANG=C
LC_ALL=C

# 使用法
usage() {
    echo "$0 <python_prog> <parameter_info.tsv>"
}

# 引数の個数チェック
if [ $# -ne 2 ]; then
    echo "Invalid arguments" >&2
    usage
    exit 1
fi

python_prog=$1			# 実行するpythonプログラムファイル
param_csv=$2 			# パラメータ情報tsvファイル

#----------------------------------------------------------------------
now=$(date +%Y%m%d_%H%M)

# 2列目がconfigファイル情報
conf_files=$(cat ${param_csv} \
		 | egrep -v "^#" \
		 | cut -d'	' -f2)
max_cnt=$(tail -1 ${param_csv} \
	       | cut -d'	' -f1)

# 1つ目のconfigに書かれている出力先にパラメータ情報tsvファイルをコピー
topconf=$(echo "$conf_files" | head -1)
outdir=$(grep "outdir" ${topconf} \
	     | tr -d ' ' \
	     | cut -d'=' -f2 \
	     | tr -d '"')
cp ${param_csv} ${outdir}/${now}_$(basename ${param_csv})

cnt=0
echo "${conf_files}" \
    | while read f; do
    echo "--------------------------------------------------"
    echo "grid: ${cnt}/${max_cnt}"
    date
    python3 ${python_prog} -c ${f} -b ${now}_${cnt}
    cnt=`expr ${cnt} + 1`
done
