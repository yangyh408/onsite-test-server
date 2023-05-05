## linux
`conda activate pack_evaluate`
`pyinstaller -F -c evaluator_linuxtool.py -p "/media/yangyh408/YangYH408/onsite-test-server/tester/evaluate" -n evaluator --add-data /media/yangyh408/YangYH408/onsite-test-server/tester/evaluate/server_v3:./server_v3 --add-data /media/yangyh408/YangYH408/onsite-test-server/tester/evaluate/ramp:./ramp`