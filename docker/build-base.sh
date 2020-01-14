
SHPATH=$(cd `dirname $0`; pwd)
BASEPATH=${SHPATH}/..
if [ ! -f "${BASEPATH}/requirements.txt" ]; then
    echo "requirements.txt not found"
	exit 1
fi

docker build -t vmp-base -f ${BASEPATH}/docker/Dockerfile ${BASEPATH}
