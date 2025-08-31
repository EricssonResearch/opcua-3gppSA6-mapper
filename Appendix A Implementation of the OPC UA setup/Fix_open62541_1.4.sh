#!/bin/bash
set -e

# Paths to files that need <stdlib.h>
FILES=(
  "$HOME/open62541/build/src_generated/open62541/config.h"
  "$HOME/open62541/examples/pubsub/tutorial_pubsub_mqtt_publish.c"
  "$HOME/open62541/examples/pubsub/tutorial_pubsub_mqtt_subscribe.c"
  "$HOME/open62541/examples/json_config/server_file_based_config.c"
)

echo "Checking and fixing missing #include <stdlib.h>..."
for f in "${FILES[@]}"; do
  if [ -f "$f" ]; then
    if ! grep -q "<stdlib.h>" "$f"; then
      # Insert after first #include line
      sed -i '/#include/ a #include <stdlib.h>' "$f"
      echo "Added #include <stdlib.h> to $f"
    else
      echo "Already has #include <stdlib.h>: $f"
    fi
  else
    echo "File not found: $f"
  fi
done

# Fix PTHREAD_MUTEX_RECURSIVE → PTHREAD_MUTEX_RECURSIVE_NP
TARGET="$HOME/open62541/examples/pubsub_realtime/server_pubsub_publisher_rt_level.c"
if [ -f "$TARGET" ]; then
  if grep -q "PTHREAD_MUTEX_RECURSIVE" "$TARGET"; then
    sed -i 's/PTHREAD_MUTEX_RECURSIVE/PTHREAD_MUTEX_RECURSIVE_NP/g' "$TARGET"
    echo "Replaced PTHREAD_MUTEX_RECURSIVE with PTHREAD_MUTEX_RECURSIVE_NP in $TARGET"
  else
    echo "No PTHREAD_MUTEX_RECURSIVE found in $TARGET"
  fi
else
  echo "File not found: $TARGET"
fi

echo "All fixes applied!"
