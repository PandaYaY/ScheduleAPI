from flask import request
from flask import send_file
from flask import jsonify

download_version = '0.1'


def get_version():
    return jsonify({'version': download_version})


def download_app():
    platform = request.args.get('platform')

    if platform == 'macos':
        return send_file(f'/home/server/appVersions/macos/{download_version}/4reich.dmg', as_attachment=True)
    elif platform == 'linux':
        return send_file(f'/home/server/appVersions/linux/{download_version}/4reich.zip', as_attachment=True)
    elif platform == 'android':
        return send_file(f'/home/server/appVersions/android/{download_version}/4reich.apk', as_attachment=True)
    elif platform == 'presentation':
        return send_file('/home/server/other_files/presentation.pptx', as_attachment=True)
    else:
        return send_file(f'/home/server/appVersions/windows/{download_version}/4reich.exe', as_attachment=True)
