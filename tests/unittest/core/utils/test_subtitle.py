import json
import textwrap

from bili_jeans.core.utils import convert_to_srt


SAMPLE_SUBTITLE = {
  "font_size": 0.4,
  "font_color": "#FFFFFF",
  "background_alpha": 0.5,
  "background_color": "#9C27B0",
  "stroke": "none",
  "body": [
    {
      "from": 0.35,
      "to": 1.6,
      "location": 2,
      "content": "5090D咱们聊完了"
    },
    {
      "from": 1.6,
      "to": 5.55,
      "location": 2,
      "content": "今天咱们就来聊聊这一代的80级别显卡——5080"
    }
  ]
}


def test_convert_to_srt():
    sample_input = json.dumps(SAMPLE_SUBTITLE).encode('utf-8')
    actual = convert_to_srt(sample_input)
    expected_str = textwrap.dedent('''\
        1
        00:00:00,350 --> 00:00:01,600
        5090D咱们聊完了

        2
        00:00:01,600 --> 00:00:05,550
        今天咱们就来聊聊这一代的80级别显卡——5080

        ''')
    assert actual == expected_str.encode('utf-8')
