# https://lsyncd.github.io/lsyncd/faq/postscript/

/usr/bin/rsync "$@"
result=$?
(
  if [ $result -eq 0 ]; then
     source ~/devsync/scripts/test_handler/test.sh;
  fi
) >/dev/null 2>/dev/null </dev/null

exit $result
