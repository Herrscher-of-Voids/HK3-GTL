"""内测5批次2：从已确认HTML提取三封信，补充中英文界面与英译资源。
Beta5 batch 2: extract approved HTML letters and install bilingual UI/localization.
变更记录 #1：2026-09-22，生成时间写入changelog；不重写已确认中文正文。
Extract paragraph text exactly (normalizing HTML line breaks only), preserving all other language keys.
无网络与外部输入；固定路径，运行前须归档目标语言文件。
Fixed local paths only, no network; archive target language files before running.
"""
from pathlib import Path
from html.parser import HTMLParser
import json

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT/'doc/HK3GTL-内测5/05_叙事事件/奥托首次来信与玩家两种回信_定稿v1.html'

class Letters(HTMLParser):
    """提取前三个h2章节中的p正文；strong仅去标记，br保留换行。 / Extract p text under the first three h2 headings, preserving br."""
    def __init__(self):
        super().__init__()
        self.section = -1
        self.paragraph = None
        self.documents = []
    def handle_starttag(self, tag, attrs):
        if tag == 'h2':
            self.section += 1
            self.documents.append([])
        if tag == 'p' and 0 <= self.section < 3:
            self.paragraph = []
        if tag == 'br' and self.paragraph is not None:
            self.paragraph.append('\n')
    def handle_data(self, data):
        if self.paragraph is not None:
            self.paragraph.append(data)
    def handle_endtag(self, tag):
        if tag == 'p' and self.paragraph is not None:
            text = ''.join(self.paragraph).strip().replace('\n\n', '\n')
            self.documents[self.section].append(text)
            self.paragraph = None

# 英译仅服务英文界面；中文定稿仍为叙事内容的权威来源。
# English localization follows the approved Chinese original, which remains authoritative.
ENGLISH = [
[
"Esteemed pioneers of another world,",
"Allow me to offer my greetings across the barriers between our worlds.",
"I am Otto Apocalypse, Overseer of Schicksal. In our world, this organization has long devoted itself to combating a calamity known as the Honkai.",
"Through the Second Divine Key left by the Previous Era, the Cosmic Juggernaut, I have had the privilege of observing your world. Frankly, a civilization that has advanced its industry and energy technology so far without relying on Honkai energy deserves any researcher's attention.",
"Yet while admiring these accomplishments, I noticed certain familiar signs.",
"An energy you have not yet identified is spreading through your world. Perhaps it has not entered your classifications of energy, or perhaps you have recorded it only as unexplained measurement discrepancies. In our world, however, it has a definite name:",
"Honkai energy.",
"According to our observations, these signs suggest that your civilization may already have drawn the attention of the Cocoon of Finality.",
"I realize that, to someone receiving their first message from another world, this may sound like a carefully prepared threat. I have therefore enclosed basic observational material describing the signatures of Honkai energy and the preliminary methods we have used to identify it. You may test these first, then decide whether to continue reading my proposal.",
"Throughout our history, the Honkai has repeatedly accompanied the advancement of civilization. Corrupted humans, creatures called Honkai Beasts, and Herrschers wielding extraordinary powers have all taught us painful lessons.",
"But I must acknowledge this: your world is not ours.",
"The disasters we have experienced may not take the same form in your world. Nor can observations through the Cosmic Juggernaut provide enough information for me to reach every conclusion on your behalf. Still, until those differences are understood, learning from existing experience is wiser than meeting the unknown unprepared.",
"I should also explain that destruction is not the only aspect of Honkai energy. We have attempted to understand, contain, and employ it. For a civilization with your mature industrial foundations, it may represent danger, but it may also open an undiscovered technological path.",
"That is why I am writing to you.",
"Schicksal possesses knowledge accumulated through long exposure to the Honkai; you possess a technological history quite different from ours. I hope we can begin with limited exchanges of information, gradually learn about one another, and discuss more specific research and trade cooperation when the time is right.",
"Your energy engineering, materials processes, and the computing capabilities supporting these achievements are of particular interest to me.",
"Of course, trust cannot arrive enclosed in a letter. I will not ask you to surrender your technology or make lasting commitments before you know Schicksal. We can first identify one modest undertaking of value to both parties, then judge whether another step is worthwhile.",
"The enclosed material does not require your acceptance of cooperation. Whatever your answer, I encourage you to examine your world carefully.",
"As for how much time will have passed here when this letter reaches you, your clocks may not provide a simple answer. Different worlds do not always keep the same pace.",
"I look forward to your reply.",
"May your development never be bound by the divine.",
"Otto Apocalypse\nOverseer of Schicksal",
"Enclosure: Basic Observations of Honkai Energy"
],
[
"Mr. Otto Apocalypse,",
"We have received your letter and the accompanying material.",
"Establishing contact with a civilization in another world is a significant event for us as well. Thank you for volunteering information about Honkai energy. It offers a previously unconsidered perspective on our world, which we will study carefully and verify independently.",
"We will not lightly dismiss the disasters you describe. But we also agree with your assessment: our worlds differ. Whether events in your world will recur here is a question that further observation and evidence must answer.",
"After consideration, we are willing to accept your invitation and establish preliminary communication with Schicksal.",
"We hope to begin with information both parties can verify and clearly defined research questions. Further exchanges of technology, computing assistance, or goods can be negotiated individually once we understand one another better.",
"Our civilization is willing to learn and to share achievements of value. However, cooperation must be voluntary, reciprocal, and respectful of our independence. Arrangements affecting either party's interests require the explicit agreement of both.",
"Your experience with the Honkai may help us avoid some detours; our independently developed industry may offer you different approaches.",
"We are willing to hear about the first undertaking you propose.",
"We hope this communication across worlds will mark the beginning of a worthwhile exchange.",
"The leader of the otherworldly civilization\nWith greetings on behalf of our civilization"
],
[
"Mr. Otto Apocalypse,",
"We have received your letter and the accompanying material.",
"Establishing contact with a civilization in another world is a significant event for us as well. Thank you for volunteering information about Honkai energy. It offers a previously unconsidered perspective on our world, which we will study carefully and verify independently.",
"We will not lightly dismiss the disasters you describe. But we also agree with your assessment: our worlds differ. Whether events in your world will recur here is a question that further observation and evidence must answer.",
"After consideration, we have decided not to accept this invitation to cooperate.",
"At present, we know too little about Schicksal, your world, and the consequences this cooperation may bring. Until these matters are properly understood, we cannot assume undefined obligations on our civilization's behalf or hastily promise exchanges of technology and resources.",
"We note your assurance that the enclosed material carries no condition of cooperation. We appreciate this goodwill and will study Honkai energy in our own way, judging its significance for our world.",
"This decision expresses no hostility toward you personally or toward Schicksal. It is our position in the face of the unknown. We must judge our civilization's direction for ourselves and accept responsibility for the consequences.",
"Thank you for your letter and for your willingness to share the experience of another world.",
"May both our civilizations find a path forward.",
"The leader of the otherworldly civilization\nWith greetings on behalf of our civilization"
]]

UI = {
    'title.0': ('来自奥托的第一封信', "Otto's First Letter"),
    'title.1': ('回信：同意合作', 'Reply: Accept Cooperation'),
    'title.2': ('回信：不同意合作', 'Reply: Decline Cooperation'),
    'locked': ('尚未收到跨界来信。', 'No otherworldly correspondence has arrived.'),
    'received': ('收到来自天命的信件。点击阅读，或输入 /hk3letter。暂不回复不会视为拒绝。', 'A letter from Schicksal has arrived. Click to read, or use /hk3letter. You may reply later.'),
    'reply_rejected': ('请先阅读首信；已经提交的回信不能重复或改选。', 'Read the first letter before replying. A submitted reply cannot be repeated or changed.'),
    'accepted': ('已寄出同意合作的回信。随信情报已保留；具体合作另行商议。', 'Your acceptance has been sent. The enclosed information is retained; specific cooperation will be negotiated separately.'),
    'declined': ('已寄出不同意合作的回信。随信情报仍然保留，你可以独立开展研究。', 'Your refusal has been sent. The enclosed information remains available for independent research.'),
    'preview_accept': ('预览同意回信', 'Preview Acceptance'),
    'preview_decline': ('预览拒绝回信', 'Preview Refusal'),
    'back': ('返回首信', 'Back to Letter'),
    'send': ('确认寄出此信', 'Confirm and Send'),
    'close': ('关闭，稍后再看', 'Close for Now'),
    'sent_reply': ('查看已寄出回信', 'Read Sent Reply'),
    'scroll': ('滚轮翻阅 · 第 %s / %s 行', 'Scroll to read · Line %s / %s')
}

def main():
    """固定源读取、段落数量校验后写入；异常直接失败，不输出占位文本。 / Validate paragraph counts before writing, never generate placeholders."""
    parser = Letters()
    parser.feed(SOURCE.read_text(encoding='utf-8'))
    chinese = parser.documents[:3]
    assert [len(d) for d in chinese] == [23,11,11]
    assert [len(d) for d in ENGLISH] == [23,11,11]
    for index, (language, documents) in enumerate([('zh_cn',chinese),('en_us',ENGLISH)]):
        path = ROOT/'src/main/resources/assets/hk3gtl/lang'/f'{language}.json'
        data = json.loads(path.read_text(encoding='utf-8'))
        for suffix, values in UI.items():
            data['hk3gtl.letter.'+suffix] = values[index]
        for doc, paragraphs in enumerate(documents):
            for i, paragraph in enumerate(paragraphs):
                data[f'hk3gtl.letter.text.{doc}.{i}'] = paragraph
        path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Installed 45 approved Chinese paragraphs and 45 English translations; 15 UI keys per language.')

if __name__ == '__main__':
    main()

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
