from datetime import datetime
from django.test import TestCase, Client
from django.urls import reverse
from .models import ImageAnalysisResult
import csv
from io import StringIO


class ImageAnalysisViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get_request(self):
        """GETリクエストが正常に処理され、適切なテンプレートが使用されることをテストする"""
        response = self.client.get(reverse('analyze-image'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'analyze_image_class/image_analysis_form.html')

    def test_post_request_with_valid_data(self):
        """有効なデータでPOSTリクエストを送信した場合の挙動をテストする"""
        url = reverse('analyze-image')  # analyze-image はフォームを表示するビューのURL名
        data = {'image_path': 'test/image.png', 'debug_mode': True}
        response = self.client.post(url, data)
        
        # リダイレクトされることを確認（ビューの実際の挙動に基づく）
        self.assertEqual(response.status_code, 302)  # or 200, depending on actual behavior

        # データが保存されたことを確認
        self.assertEqual(ImageAnalysisResult.objects.count(), 1)
        result = ImageAnalysisResult.objects.first()
        self.assertEqual(result.image_path, 'test/image.png')


    def test_post_request_with_invalid_data(self):
        """無効なデータでPOSTリクエストを送信した場合、エラーが表示されることをテストする"""
        url = reverse('analyze-image')
        response = self.client.post(url, {})  # 空のデータを送信

        self.assertEqual(response.status_code, 200)  # ステータスコードが200であることを確認
        # レスポンスのコンテキストからフォームを取得
        form = response.context['form']
        # フォームのエラーを検証
        self.assertTrue(form.errors)


    def test_csv_export(self):
        """CSVエクスポート機能をテスト"""
        # テストデータを作成
        ImageAnalysisResult.objects.create(image_path='test.jpg', success=True, message='Test', class_id=1, confidence=0.99, request_timestamp=datetime.now(), response_timestamp=datetime.now())

        # CSVエクスポートの実行
        response = self.client.get(reverse('export-csv'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Type'), 'text/csv')
        content = response.content.decode('utf-8')
        csv_reader = csv.reader(StringIO(content))
        rows = list(csv_reader)
        self.assertGreater(len(rows), 1)
