#!/bin/sh

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
