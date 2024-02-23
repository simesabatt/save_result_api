from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import View
from .models import ImageAnalysisResult
from .forms import ImagePathForm
import csv
from datetime import datetime
import requests
import random

def mock_analyze_image_api(image_path):
    """
    画像分析APIのモック関数。特定の確率で成功または失敗のレスポンスを返す。
    """
    FAILURE_RATE = 0.33 # ３回に一回失敗する設定
    if random.random() < FAILURE_RATE:
        return {
            'success': False,
            'message': 'Test error',
            'estimated_data': 0  # 失敗時は0を返す
        }
    else:
        return {
            'success': True,
            'message': 'Test analysis succeeded',
            'estimated_data': {
                'class': 3,
                'confidence': 0.95
            }
        }


def analyze_image_api(image_path):
    """
    実際の画像分析APIにリクエストを送信し、レスポンスを返す関数。
    """
    url = "http://example.com/"
    payload = {'image_path': image_path}
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()  # HTTPエラーがある場合の例外
        return response.json()
    except requests.RequestException as e:
        # 例外をキャッチし、エラーメッセージを含む辞書を返す
        return {
            'success': False,
            'message': str(e),
            'estimated_data': 0
        }


class ImageAnalysisView(View):
    """
    画像分析リクエストのためのビュー。GETリクエストでフォームを表示し、
    POSTリクエストで画像分析を実行する。
    """
    def get(self, request, *args, **kwargs):
        form = ImagePathForm(initial={'debug_mode': request.session.get('debug_mode', False)})
        results_list = ImageAnalysisResult.objects.all()  # 結果リストのデータを取得
        return render(request, 'analyze_image_class/image_analysis_form.html', {
            'form': form,
            'results_list': results_list,  # 結果リストをテンプレートに渡す
        })

    def post(self, request, *args, **kwargs):
        form = ImagePathForm(request.POST)
        if form.is_valid():
            image_path = form.cleaned_data['image_path']
            debug_mode = form.cleaned_data['debug_mode']

            # デバッグモードの状態をセッションに保存
            request.session['debug_mode'] = debug_mode

            # リクエスト送信前の時刻を記録
            request_timestamp = datetime.now()

            if debug_mode:
                response_data = mock_analyze_image_api(image_path)
            else:
                response_data = analyze_image_api(image_path)

            # レスポンス受信後の時刻を記録
            response_timestamp = datetime.now()

            if response_data and isinstance(response_data, dict):
                ImageAnalysisResult.objects.create(
                    image_path=image_path,
                    success=response_data['success'],
                    message=response_data.get('message', ''),
                    class_id=response_data.get('estimated_data', {}).get('class') if response_data['success'] else None,
                    confidence=response_data.get('estimated_data', {}).get('confidence') if response_data['success'] else None,
                    request_timestamp=request_timestamp,
                    response_timestamp=response_timestamp
                )

                # 成功した場合のメッセージ
                if response_data['success']:
                    messages.success(request, '画像分析が正常に完了しました。')
                else:
                    # 失敗した場合のメッセージ
                    messages.error(request, f"エラーが発生しました: {response_data.get('message', '')}")
            else:
                # APIリクエストが失敗した場合、エラーメッセージをセット
                error_message = "APIリクエストに失敗しました。"
                messages.error(request, error_message)

                ImageAnalysisResult.objects.create(
                    image_path=image_path,
                    success=False,
                    message=error_message,
                    class_id=None,
                    confidence=None,
                    request_timestamp=request_timestamp,
                    response_timestamp=response_timestamp
                )

            return redirect('analyze-image')
        else:
            # 無効なデータでPOSTリクエストを送信した場合の処理
            results_list = ImageAnalysisResult.objects.all()  # 結果リストのデータを再取得
            return render(request, 'analyze_image_class/image_analysis_form.html', {'form': form, 'results_list': results_list})


class ExportImageAnalysisResultsCSVView(View):
    """
    画像分析結果をCSVファイルとしてエクスポートするビュー。
    """
    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="image_analysis_results.csv"'
        writer = csv.writer(response)
        writer.writerow(['Image Path', 'Success', 'Message', 'Class ID', 'Confidence', 'Request Timestamp', 'Response Timestamp'])
        results = ImageAnalysisResult.objects.all()
        for result in results:
            writer.writerow([
                result.image_path, result.success, result.message, result.class_id, 
                result.confidence, result.request_timestamp.strftime('%Y-%m-%d %H:%M:%S'), 
                result.response_timestamp.strftime('%Y-%m-%d %H:%M:%S')
            ])
        return response
