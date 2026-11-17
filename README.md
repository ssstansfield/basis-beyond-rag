# Basis & Beyond 路 鍙屼功 RAG

**Start here:** open [`Start_RAG.ipynb`](Start_RAG.ipynb), select a **Python 3.12** kernel and choose **Run All**. The notebook prepares the environment, restores the included knowledge base and displays the app inline with a link to open it in a tab. Initial setup needs internet access to download dependencies and the embedding model. Later runs reuse the local cache.

The interface defaults to **English**. Select **涓枃** in the sidebar to switch the interface and new answers to Chinese. Original book passages retain their original language. For **Light / Dark / System**, use the **鈰?menu** in the top-right corner.

**鎺ㄨ崘鍏ュ彛锛?*鎵撳紑 [`Start_RAG.ipynb`](Start_RAG.ipynb)锛岄€夋嫨 Python 3.12 鍐呮牳锛岀偣鍑汇€屽叏閮ㄨ繍琛屻€嶃€傚畠浼氬噯澶囦緷璧栥€佹仮澶嶉寤虹煡璇嗗簱銆佸惎鍔ㄥ簲鐢紝骞跺湪 Notebook 鍐呭睍绀虹晫闈紱涔熷彲浠ョ偣鍑婚摼鎺ュ湪鏂版爣绛鹃〉鎵撳紑銆傞噸澶嶈繍琛屽惎鍔ㄥ崟鍏冩牸浼氬鐢ㄥ悓涓€涓繘绋嬶紱鎸?Notebook 璇存槑杩愯 `rag.stop()` 鍙仠姝€傞渶瑕佸湪娴忚鍣ㄦ墍鍦ㄧ數鑴戞湰鍦拌繍琛?Jupyter锛岃繙绋嬩簯 Notebook 鐨?localhost 涓嶆寚鍚戞湰鏈恒€?
椤圭洰鍖呭惈涓ゆ湰 PDF 鍙?`knowledge/` 涓殑棰勫缓绱㈠紩銆傝繍琛屾椂鐨?`data/`銆佹ā鍨嬬紦瀛樸€佽櫄鎷熺幆澧冨拰涓存椂鏃ュ織鍧囧湪 `.gitignore` 涓€傛湰鍦?Git 浠撳簱宸插噯澶囷紝鎸夋湰娆¤姹傛湭鍒涘缓杩滅銆佹湭鎺ㄩ€併€?
鏈湴杩愯鐨勪腑鑻辨枃涔︾睄闂瓟搴旂敤銆傜幇闃舵鐨勭煡璇嗛鍩熸槸锛?*缇庡浗鍥藉€虹幇璐т笌鏈熻揣銆佸熀宸笌浜ゅ壊銆佸鍒╀氦鏄擄紝浠ュ強 LTCM 妗堜緥涓殑鏉犳潌銆佹祦鍔ㄦ€т笌椋庨櫓绠＄悊**銆?
鐭ヨ瘑鏉ユ簮涓?`books/` 涓嬬殑銆奣he Treasury Bond Basis銆嬶紙312 椤碉級鍙娿€婅祵閲戣€咃細闀挎湡璧勬湰绠＄悊鍏徃鐨勫崌鑵句笌闄ㄨ惤銆嬶紙314 椤碉級銆傚師 PDF 淇濇寔鍘熸牱銆傜郴缁熷紩鐢?**浠?1 寮€濮嬬殑 PDF 鐗╃悊椤电爜**锛屼笉鏄功涓婂嵃鍒烽〉鐮併€?
褰撳墠宸插缓绔?**3,902 涓墖娈点€?84 缁?FAISS 绱㈠紩**锛氳嫳鏂囦功 1,976 涓墖娈碉紝涓枃涔?1,926 涓墖娈碉紱涓枃涔?27 椤电敱 OCR 琛ュ厖銆?
## 鍚姩

鍦?PowerShell 涓繘鍏ユ湰椤圭洰锛?
```powershell
.\start.ps1
```

鐒跺悗璁块棶 <http://127.0.0.1:8050>銆?050 鐢ㄤ簬閬垮紑鏈満 Windows 瀵?8501 绛夌鍙ｇ殑淇濈暀銆傝嫢绔彛琚崰鐢紝浣跨敤涓嬮潰鐨勫懡浠よ嚜琛屾寚瀹氱┖闂茬鍙ｏ細

```powershell
.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1 --server.port 8051 --browser.gatherUsageStats false
```

鐣岄潰鏈夌煡璇嗛鍩熶粙缁嶃€侀棶棰樿緭鍏ユ銆佺ず渚嬮棶棰樸€佷功绫嶇瓫閫夈€佸洖绛斿強鍙睍寮€鐨勫師鏂囪瘉鎹€傛彁渚涖€孋odex 闂瓟銆嶅拰銆屼粎妫€绱㈠師鏂囥€嶄袱绉嶆ā寮忋€備粎妫€绱㈡棤闇€鐧诲綍锛涢棶绛斾娇鐢ㄨ繖鍙扮數鑴戝凡鐧诲綍鐨?Codex CLI銆?
## 浠庡ご瀹夎涓庡缓搴?
瑕佹眰 Python 3.12銆丆odex CLI锛涢娆′笅杞戒緷璧栧拰 embedding 妯″瀷闇€瑕佽仈缃戙€?
```powershell
uv venv --python 3.12 .venv
uv pip install --python .venv\Scripts\python.exe -r requirements.lock.txt
codex login
.venv\Scripts\python.exe -m src.ingest
.\start.ps1
```

娌℃湁 `uv` 鏃跺彲浠ョ敤 `python -m venv .venv` 鍜?`.venv\Scripts\python.exe -m pip install -r requirements.lock.txt`銆傚紑鍙戦獙璇佸彟琛屽畨瑁?`requirements-dev.txt`锛堝寘鍚?pytest銆丯otebook 鎵ц鍙婃祻瑙堝櫒娴嬭瘯宸ュ叿锛夈€?
鎶婃柊澧炴垨鏇存柊鐨?PDF 鏀捐繘 `books/` 鍚庨噸鏂版墽琛?`python -m src.ingest`銆傛枃浠跺搱甯屽拰娴佹按绾块厤缃笉鍙樻椂澶嶇敤鏁翠釜绱㈠紩锛涢噸鏂板缓搴撴椂鎸夋枃鏈鐢ㄥ凡鏈夊悜閲忋€俙--force` 寮哄埗閲嶆柊澶勭悊鏂囨湰锛屼粛澶嶇敤鐩稿悓妯″瀷涓嬬殑宸叉湁鍚戦噺銆傛洿鎹㈡ā鍨嬫垨鍒嗗潡鍙傛暟鍚庝細閲嶅缓銆傛棫绱㈠紩浠ｄ繚鐣欏湪 `data/`锛屾柊浠ｅ啓鍏ユ垚鍔熷悗鎵嶅師瀛愬垏鎹?`data/CURRENT`銆?
## 鍦?Codex 鍐呮绱?
鏈満宸叉敞鍐屽悕涓?`books-rag` 鐨勫叏灞€ MCP 鏈嶅姟銆?*鏂板缓鎴栭噸鍚?Codex 浼氳瘽**鍚庝娇鐢?`/mcp` 鏌ョ湅鏈嶅姟銆傚綋鍓嶅凡杩愯鐨勫璇濆彲鑳介渶瑕侀噸鏂板姞杞藉伐鍏枫€?
鍦ㄥ叾浠栨満鍣ㄤ笂锛屾浛鎹互涓嬩袱涓粷瀵硅矾寰勫苟杩愯锛?
```powershell
codex mcp add books-rag -- 'C:\Users\stansfield\Documents\Coding\RAG\.venv\Scripts\python.exe' 'C:\Users\stansfield\Documents\Coding\RAG\mcp_entry.py'
```

鏈嶅姟鎻愪緵涓変釜鍙宸ュ叿锛?
- `list_books()`锛氭煡鐪嬩功绫嶅強 `book_id`銆?- `search_books(query, book_id?, top_k=6)`锛氫腑鑻辨枃璇箟妫€绱紝鏈€澶?12 涓墖娈点€?- `get_chunk(chunk_id)`锛氬彇鍥炲叿浣撶墖娈典笌鍑哄銆?
鍙洿鎺ュ Codex 璇达細銆屼娇鐢?books-rag 鐭ヨ瘑搴擄紝瑙ｉ噴 CTD锛屽苟寮曠敤鍘熶功 PDF 椤电爜銆傘€峂CP 妫€绱笉璋冪敤璇█妯″瀷锛汣odex 鑷繁鏍规嵁杩斿洖鐨勫師鏂囦綔绛斻€傚畠涓庣綉椤典娇鐢ㄧ浉鍚岀殑绱㈠紩銆?
## 鏁版嵁鍜屽洖绛旀祦绋?
```text
PDF 鈫?閫愰〉鎻愬彇姝ｆ枃 / 鍥剧墖椤垫湰鍦?OCR 鈫?娓呯悊閲嶅椤电湁椤佃剼
    鈫?鎸夌湡瀹?tokenizer 鍒嗗潡 鈫?鏈湴 ONNX embedding
    鈫?FAISS锛堝綊涓€鍖栧悜閲忓唴绉級+ SQLite锛堝師鏂囥€佷功鍚嶃€佺珷鑺傘€侀〉鐮侊級

鐣岄潰闂 鈫?FAISS 妫€绱?鈫?鍘熸枃鐗囨 + 鐢ㄦ埛闂 鈫?codex exec 鈫?甯?[S1] 寮曠敤鐨勫洖绛?Codex 瀵硅瘽 鈫?MCP 宸ュ叿 鈫?鍚屼竴 FAISS / SQLite 鈫?Codex 缁勭粐鍥炵瓟
```

Embedding 妯″瀷涓?`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`锛?84 缁达紝鏀寔涓嫳鏂囪法璇█妫€绱€傛ā鍨嬭緭鍏ラ檺鍒?128 tokens锛屽洜姝ゆ鏂囩墖娈典笂闄愪负 **112 tokens锛岄噸鍙?20 tokens**锛屽敖閲忓湪鍙ユ湯鍒囧垎锛岀墖娈典笉璺ㄩ〉銆傝繖閲岀殑 token 鐢辫妯″瀷鐨?tokenizer 璁＄畻锛屼笉鑳界洿鎺ユ崲鎴愬ぇ妯″瀷鐨?token 鏁般€傛绱㈡渶澶氫繚鐣欐瘡椤典袱涓墖娈碉紝鍑忓皯閲嶅彔鍗犳弧缁撴灉銆?
鍥剧墖涓旀鏂囧緢灏戠殑椤甸潰浣跨敤鏈湴 RapidOCR 琛ュ厖锛孫CR 缁撴灉鎸?PDF 鍝堝笇鍙婇〉鐮佺紦瀛樸€傜晫闈細鏍囪 OCR 鐗囨銆傛爣棰?灏侀潰鎴栫┖鐧介〉鍙兘娌℃湁鍙敤鍐呭锛涘浘琛ㄣ€佸鏉傚叕寮忋€佹暟瀛楀拰 OCR 鏂囧瓧闇€瑕佸鐓у師 PDF銆傞儴鍒嗙珷鑺傜敱 PDF 涔︾鎴栦腑鏂囩珷鏍囬璇嗗埆锛涙病鏈夊彲闈犵珷鑺備俊鎭椂浠嶆彁渚涗功鍚嶅拰椤电爜銆?
缃戦〉閫氳繃 `codex exec` 闈炰氦浜掓ā寮忕敓鎴?JSON 鏍煎紡鍥炵瓟锛屾牎楠屽紩鐢ㄧ紪鍙锋槸鍚︽潵鑷湰娆℃绱€傝瘉鎹笉瓒虫椂搴旀槑纭鏄庯紝涓嶅皢鐩镐技搴﹀綋浣滄纭鐜囥€備娇鐢ㄥ崟娆′复鏃?Codex 浼氳瘽锛屼笉鑷姩缁ф壙鍏朵粬 MCP 鏈嶅姟銆傜綉椤靛彧淇濈暀褰撳墠浼氳瘽涓殑鏈€杩戜竴娆￠棶棰樹笌鍥炵瓟銆?
**鏁版嵁鍘诲悜锛?*涔︾睄瑙ｆ瀽銆丱CR銆乪mbedding 鍜屾绱㈠潎鍦ㄦ湰鍦板畬鎴愶紱鐐瑰嚮銆孋odex 闂瓟銆嶆椂锛岄棶棰樹笌鏈鍙洖鐨勭墖娈典細鍙戠粰 Codex銆傛ā鍨嬬紦瀛樺拰绱㈠紩浣嶄簬 `data/`锛屾湭灏嗕功绫嶄笂浼犲埌鎵樼缃戠珯銆?
## 楠岃瘉

```powershell
.venv\Scripts\python.exe -m pytest tests -q
.venv\Scripts\python.exe scripts\check_mcp.py
.venv\Scripts\python.exe scripts\check_codex.py
.venv\Scripts\python.exe scripts\check_notebook.py
.venv\Scripts\python.exe scripts\check_browser.py
```

`check_codex.py` 浼氱湡瀹炶皟鐢ㄥ凡鐧诲綍鐨?Codex锛屾鏌ュ浗鍊洪棶绛斻€丩TCM 闂瓟銆佺煡璇嗗簱澶栭棶棰樼殑璇佹嵁涓嶈冻鍝嶅簲锛屼互鍙婁竴涓柊 Codex 浼氳瘽鏄惁瀹為檯璋冪敤宸叉敞鍐?MCP銆傞渶瑕佺綉缁滃苟娑堣€?Codex 鐢ㄩ噺銆傚畠鐨勬湰鍦扮粨鏋滃湪 `tmp/`銆俙check_notebook.py` 鎵ц鐪熷疄鍏ュ彛 Notebook锛岄獙璇佸惎鍔ㄣ€佽繘绋嬪鐢ㄤ笌鍋滄銆俙check_browser.py` 瑕佹眰鏈満瀹夎 Chrome 骞跺凡鍚姩缃戦〉锛岄獙璇佹槑鏆椾富棰樼殑鏂囧瓧瀵规瘮搴︺€佷腑鑻辨枃鍒囨崲鍜屽疄闄呮绱氦浜掋€?
`tests/` 妫€鏌ヤ腑鑻辨枃鍒嗗潡闀垮害銆佺湡瀹炰功绫嶆绱笌绛涢€夈€佷笉瀛樺湪寮曠敤鐨勬嫤鎴紝浠ュ強 Streamlit 杈撳叆銆佹彁浜ゃ€佸師鏂囧睍绀烘祦绋嬨€傛绱㈠拰寮曠敤妫€鏌ユ棤娉曡瘉鏄庢墍鏈夌敓鎴愬唴瀹归兘姝ｇ‘锛屽挨鍏舵槸璺ㄧ墖娈佃绠楁垨澶嶆潅琛ㄦ牸闂銆?
2026-11-17 楠岃瘉缁撴灉锛? 椤?pytest 娴嬭瘯閫氳繃锛堝惈榛樿鑻辨枃銆佷腑鑻辨枃鍒囨崲鍚庝繚鐣欓棶棰樹笌缁撴灉銆佹寜鎵€閫夎瑷€鐢熸垚鍥炵瓟锛夛紱鍏ュ彛 Notebook 宸插畬鏁存墽琛岋紝鍚姩銆佸鐢ㄣ€佸仠姝㈡鏌ラ€氳繃锛涚嫭绔?Chrome 涓?Light / Dark 涓婚瀵规瘮搴︽鏌ャ€佷腑鑻辨枃鍒囨崲鍙婂師鏂囨绱㈤€氳繃锛屽苟妫€鏌ヤ簡鎴浘銆傚闂存ā寮忎慨澶嶇Щ闄や簡鍥哄畾鐨勬祬鑹茶儗鏅拰娣辫壊鏂囧瓧锛屾墍鏈夋枃瀛椼€佽緭鍏ユ涓庝晶鏍忚窡闅忓師鐢熶富棰橈紱鑷畾涔夊崱鐗囦娇鐢ㄧ户鎵块鑹诧紝涓嶄緷璧栧綋鍓嶇増鏈湭鎻愪緵鐨勬棫 CSS 鍙橀噺銆傛鍓?MCP 涓変釜宸ュ叿銆佺湡瀹?Codex 闂瓟鍜屾柊浼氳瘽 MCP 璋冪敤涔熷凡閫氳繃銆?
## 鏂囦欢缁撴瀯

```text
app.py                  Streamlit 闂瓟鐣岄潰
Start_RAG.ipynb          鎺ㄨ崘鍏ュ彛锛氬噯澶囩幆澧冨苟鍐呭祵鍚姩鐣岄潰
knowledge/              鍙惡甯︾殑褰撳墠鐭ヨ瘑搴撳揩鐓?start.ps1               鏈湴鍚姩鑴氭湰
mcp_entry.py            涓庡伐浣滅洰褰曟棤鍏崇殑 MCP 鍏ュ彛
src/ingest.py           鎻愬彇 / OCR / 鍒嗗潡 / 寤哄簱
src/embedding.py        鏈湴 embedding 涓?tokenizer
src/retrieve.py         鍏辩敤妫€绱㈤€昏緫
src/codex_client.py     Codex 鍥炵瓟涓庡紩鐢ㄧ紪鍙锋牎楠?src/i18n.py             鑻辨枃 / 涓枃鐣岄潰鏂囨
src/mcp_server.py       MCP 鍙宸ュ叿
data/CURRENT            褰撳墠绱㈠紩浠?data/index-*/           FAISS銆丼QLite 鍜?manifest
data/models/            鏈湴妯″瀷缂撳瓨
data/ocr/               OCR 缂撳瓨
tests/                  搴旂敤娴嬭瘯
scripts/                MCP 涓?Codex 闆嗘垚楠岃瘉
```

鎶€鏈緷鎹細[FastEmbed 鏀寔鐨勬ā鍨媇(https://qdrant.github.io/fastembed/examples/Supported_Models/)銆乕FAISS](https://github.com/facebookresearch/faiss)銆乕Codex MCP](https://developers.openai.com/codex/mcp)銆乕Codex 闈炰氦浜掕皟鐢╙(https://developers.openai.com/codex/noninteractive)銆乕RapidOCR](https://github.com/RapidAI/RapidOCR)銆?
