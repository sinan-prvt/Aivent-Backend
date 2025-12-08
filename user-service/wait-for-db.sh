set -e

DB_HOST=$1
DB_PORT=$2

echo "Waiting for PostgreSQL at $DB_HOST:$DB_PORT ..."

while ! nc -z $DB_HOST $DB_PORT; do
  echo "Postgres not ready yet..."
  sleep 1
done

echo "Postgres is up."

shift 2

exec "$@"
