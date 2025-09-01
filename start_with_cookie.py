��#!/usr/bin/env python3

# -*- coding: utf-8 -*-

"""

&^Cookie�{t�R���v/T�R�,g

Start script with cookie management features

"""



import os

import sys

import uvicorn

import argparse

from datetime import datetime



# O(u�~N�v_M�n

from path_config import setup_project_paths

setup_project_paths()



import sys

from pathlib import Path



# nx�Oy��v9h�vU_(W_-N

project_root = Path(__file__).parent

if str(project_root) not in sys.path:

    sys.path.insert(0, str(project_root))



from database import db_manager

from cookie_manager import cookie_manager



def check_cookie_status():

    """�h�gCookie�r`"""

    print("=" * 50)

    print("Cookie�r`�h�g")

    print("=" * 50)

    

    try:

        status = cookie_manager.get_cookie_status()

        

        if status['has_cookie']:

            if status['is_expired']:

                print("�&�  Cookie�]Ǐg��^���f�e")

                print("   �S�N�Ǐ�NN�e_�f�eCookie:")

                print("   1. �(uAPI: POST /api/cookie/update_cookie")

                print("   2. O(uAitable.ai API: POST /api/aitable/sync_data")

            else:

                print("' Cookieck8^")

                if status['expires_at']:

                    print(f"   Ǐg�e��: {status['expires_at']}")

        else:

            print("L' *g��nCookie")

            print("   ��HQ��nCookieMb��ck8^O(uAPI�R��")

            print("   �S�N�Ǐ�NN�e_��nCookie:")

            print("   1. �(uAPI: POST /api/cookie/update_cookie")

            print("   2. O(uAitable.ai API: POST /api/aitable/sync_data")

        

        return status['has_cookie'] and not status['is_expired']

        

    except Exception as e:

        print(f"L' Cookie�r`�h�g1Y%�: {e}")

        return False



def initialize_database():

    """R�YSpenc�^"""

    print("=" * 50)

    print("penc�^R�YS")

    print("=" * 50)

    

    try:

        db_manager.init_database()

        print("' penc�^R�YS�[b")

        return True

    except Exception as e:

        print(f"L' penc�^R�YS1Y%�: {e}")

        return False



def show_startup_info():

    """>f:y/T�R�Oo`"""

    print("=" * 50)

    print("�b�/TikTokN}�API - &^Cookie�{t")

    print("Douyin/TikTok Download API - with Cookie Management")

    print("=" * 50)

    print(f"/T�R�e��: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    print("=" * 50)



def show_api_endpoints():

    """>f:yAPI�z�p�Oo`"""

    print("\n=��� ;N��API�z�p:")

    print("   =�� Cookie�{t:")

    print("      GET  /api/cookie/status          - ���SCookie�r`")

    print("      POST /api/cookie/update_cookie   - �f�eCookie")

    print("      GET  /api/cookie/test            - KmՋCookie")

    print("      DELETE /api/cookie/clear         - nd�Cookie")

    print("      GET  /api/cookie/history         - Cookie�S�S")

    print("   =�� Aitable.aiƖb:")

    print("      POST /api/aitable/blogger_cookie - TekZS;NCookie�Oo`")

    print("      GET  /api/aitable/get_users      - ���S@b	gZS;N�Oo`")

    print("      PUT  /api/aitable/update_user    - �f�eZS;N�Oo`")

    print("   <إ� Ɖ���S͑:")

    print("      GET  /api/douyin/fetch_user_new_videos - ���S(u7b�eƉ����S͑	�")

    print("   =��� �S	g�R��:")

    print("      GET  /api/douyin/web/fetch_user_post_videos - ���S(u7bƉ��")

    print("      GET  /api/douyin/web/fetch_one_video       - ���SUS*NƉ��")

    print("      ... 访问API文档: http://localhost:8501/docs")



def show_aitable_info():

    """>f:yAitable.aiƖb�Oo`"""

    print("\n=�� Aitable.aiƖb�Oo`:")

    print("   /ec�ǏAPITekCookie�TZS;N�Oo`:")

    print("   URL: http://localhost:8501/api/aitable/blogger_cookie")

    print("   �e�l: POST")

    print("   ��BlSO<h_:")

    print("   {")

    print('     "recordId": "recvT3eLiaaE4",')

    print('     "fields": {')

    print('       "Blogger": "g�T�[bKN�",')

    print('       "user_id": "MS4wLjABAAAAzdUNicnvSbYj3AfLtAhThVtATHyveJSaAE9hm0ul1_w",')

    print('       "cookie": "hevc_supported=true; s_v_web_id=verify_mecdiydz_Rpzrmy9K_gwM3_4ryS_8uu0_AJo9SrtOUJid; ..."')

    print("     }")

    print("   }")

    print("\n   =ء� �S�N(WAitable.ai-NM�nꁨRSĉR�(udkAPI")



def start_server(host="127.0.0.1", port=80, reload=False):

    """/T�R
g�RhV"""

    print("=" * 50)

    print("/T�R
g�RhV...")

    print("=" * 50)

    

    try:

        # >f:y/T�R�Oo`

        show_startup_info()

        

        # R�YSpenc�^

        if not initialize_database():

            print("L' penc�^R�YS1Y%���e�l/T�R
g�RhV")

            return False

        

        # �h�gCookie�r`

        cookie_ok = check_cookie_status()

        

        # >f:yAPI�z�p�Oo`

        show_api_endpoints()

        

        # >f:yAitable.aiƖb�Oo`

        show_aitable_info()

        

        print("\n" + "=" * 50)

        print("
g�RhV/T�R-N...")

        print(f"���0W@W: http://{host}:{port}")

        print(f"API�ech: http://{host}:{port}/docs")

        print("	c Ctrl+C \Pbk
g�RhV")

        print("=" * 50)

        

        # /T�RFastAPI
g�RhV

        uvicorn.run(

            "app.main:app",

            host=host,

            port=port,

            reload=reload,

            log_level="info"

        )

        

        return True

        

    except KeyboardInterrupt:

        print("\n\n=��� 
g�RhV�]\Pbk")

        return True

    except Exception as e:

        print(f"\nL' 
g�RhV/T�R1Y%�: {e}")

        return False



def main():

    """;N�Qpe"""

    parser = argparse.ArgumentParser(description="&^Cookie�{t�v�b�/TikTokN}�API/T�R�,g")

    parser.add_argument("--host", default="127.0.0.1", help="
g�RhV;N:g0W@W (؞��: 127.0.0.1)")

    parser.add_argument("--port", type=int, default=80, help="
g�RhV�z�S (؞��: 80)")

    parser.add_argument("--reload", action="store_true", help="/T(uꁨR͑}� (_�S!j_)")

    parser.add_argument("--check-cookie", action="store_true", help="�N�h�gCookie�r`")

    parser.add_argument("--init-db", action="store_true", help="�NR�YSpenc�^")

    

    args = parser.parse_args()

    

    if args.check_cookie:

        # �N�h�gCookie�r`

        check_cookie_status()

        return 0

    

    elif args.init_db:

        # �NR�YSpenc�^

        show_startup_info()

        success = initialize_database()

        if success:

            print("' penc�^R�YS�[b")

            return 0

        else:

            print("L' penc�^R�YS1Y%�")

            return 1

    

    else:

        # /T�R�[te
g�RhV

        success = start_server(args.host, args.port, args.reload)

        return 0 if success else 1



if __name__ == "__main__":

    exit_code = main()

    sys.exit(exit_code)

