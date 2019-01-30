#!/bin/sh

LANG=C
LC_ALL=C


# 使用法
usage() {
    echo "$0 <parameter_info.csv>"
}

# 引数の個数チェック
if [ $# -ne 1 ]; then
    echo "Invalid arguments" >&2
    usage
    exit 1
fi

# パラメータ情報csvファイル
param_csv=$1


#----------------------------------------------------------------------
now=$(date +%Y%M%d_%H%M)

# 2列目がconfigファイル情報
conf_files=$(cat $param_csv \
		 | egrep -v "^#" \
		 | cut -d',' -f2)
max_cnt=$(tail -1 $param_csv \
	       | cut -d',' -f1)

cnt=0
echo "$conf_files" \
    | while read f; do
    echo "--------------------------------------------------"
    echo "grid: $cnt/$max_cnt"
    date
    cnt=`expr $cnt + 1`
    python3 main.py -c $f -b ${now}_${cnt}
done
