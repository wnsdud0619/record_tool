1. event, manual 폴더명으로 폴더 생성   2.와 같은 구조로 폴더 만들어야함. 
2. event - [날짜1] - A.bag, A.yaml
	 - [날짜2] - B.bag, B.yaml
    	 - [날짜2] - C.bag, C.yaml 

    manual - D.bag, D.yaml, E.bag, E.yaml
3. NAS는 마운트 되어 있다고 가정
4. 실행은 upload.sh
   -> $ python upload_data.py [event manual 있는 경로] [NAS경로]
   -> ex)$ python upload_data.py /home/dgist/record_tool/src/record_tool/src /media/intern

