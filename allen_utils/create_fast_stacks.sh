USAGE="$0 --projectroot <PROJECT_ROOT> --owner <OWNER> --outputStackPrefix <PREFIX> --project YOURPROJECTNAME"

options=$(getopt -n $0 -l projectroot:,owner:,outputStackPrefix:: -- v "$@")
eval set -- "$options"
PREFIX=ACQ
while true; do
	case "$1" in
		--projectroot)
			shift
			PROJECT_ROOT=$1;;
		--owner)
			shift
			OWNER=$1;;
		--outputStackPrefix)
			shift
			PREFIX=$1;;
		--)
			shift
			break;;
		*)
			echo $USAGE
	esac
	shift
done
shift $((OPTIND-1))
PROJECT=$(basename $PROJECT_ROOT)

echo $PROJECT_ROOT
echo $PROJECT

python /data/array_tomography/ForSharmi/allen_SB_code/MakeAT/make_state_table_ext_multi.py --projectDirectory $PROJECT_ROOT --outputFile $PROJECT_ROOT/scripts/statetable

docker exec -t renderapps python renderapps/import/create_fast_stacks.py\
 --statetableFile $PROJECT_ROOT/scripts/statetable\
 --render.owner $OWNER\
 --render.project $PROJECT\
 --projectDirectory $PROJECT_ROOT\
 --outputStackPrefix $PREFIX\
 --render.host ibs-forrestc-ux1\
 --render.client_scripts /var/www/render/render-ws-java-client/src/main/scripts\
 --render.port 8080\
 --render.memGB 5G\
 --log_level INFO
