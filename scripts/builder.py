# -*- coding: utf-8 -*-
"""
special-ed-voice-exam: 通用特教語音互動適性試卷生成器
支援國語文、數學、生活常規各學科
"""
import os
import sys
import json
import base64
import asyncio
import edge_tts

DEFAULT_VOICE = "zh-TW-HsiaoChenNeural" # 溫暖親切的臺灣國語女聲
DEFAULT_RATE = "-5%" # 語速放慢 5%

def get_base64_from_file(file_path, mime_type="image/png"):
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            return f"data:{mime_type};base64," + base64.b64encode(f.read()).decode('utf-8')
    return ""

async def synthesize_edge_tts(key, text, cache_dir, voice=DEFAULT_VOICE, rate=DEFAULT_RATE):
    os.makedirs(cache_dir, exist_ok=True)
    file_path = os.path.join(cache_dir, f"{key}.mp3")
    if not os.path.exists(file_path):
        communicate = edge_tts.Communicate(text, voice, rate=rate)
        await communicate.save(file_path)
    return get_base64_from_file(file_path, "audio/mp3")

def math_to_spoken_chinese(text):
    """
    將數學常見算式符號轉為自然流利的臺灣教學口語
    """
    replacements = [
        (" + ", "加"),
        (" - ", "減"),
        (" * ", "乘以"),
        (" / ", "除以"),
        (" = ", "等於"),
        ("＋", "加"),
        ("－", "減"),
        ("＝", "等於"),
        (" x ", "乘以"),
        (" × ", "乘以"),
        (" ÷ ", "除以"),
        ("?", "多少"),
        ("？", "多少"),
        ("$", "")
    ]
    for old, new in replacements:
        text = text.replace(old, new)
    return text

def build_standalone_html(exam_data, sys_audio_dict, icon_emoji="📝", subject_tag="特教適性評量"):
    json_data_str = json.dumps(exam_data, ensure_ascii=False)
    sys_audio_str = json.dumps(sys_audio_dict, ensure_ascii=False)

    return f'''<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{exam_data.get("title", "特教語音互動適性試卷")} (Edge-TTS 臺灣真人語音版)</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700;900&display=swap');
    body {{
      font-family: 'Noto Sans TC', 'Microsoft JhengHei', sans-serif;
      user-select: none;
      -webkit-user-select: none;
    }}
    .card-selected {{
      border-color: #2563eb !important;
      background-color: #eff6ff !important;
      box-shadow: 0 8px 24px 0 rgba(37, 99, 235, 0.28) !important;
      transform: scale(1.01);
    }}
  </style>
</head>
<body class="bg-slate-100 text-slate-800 min-h-screen flex flex-col items-center p-3 md:p-6">

  <!-- 頂部資訊列 -->
  <header class="w-full max-w-4xl bg-white rounded-3xl shadow-md border border-slate-200 p-4 mb-4">
    <div class="flex flex-wrap items-center justify-between gap-3">
      <div class="flex items-center space-x-3">
        <span class="text-4xl">{icon_emoji}</span>
        <div>
          <h1 class="text-xl md:text-2xl font-black text-blue-900 tracking-wide">{exam_data.get("title", "特教語音互動適性試卷")}</h1>
          <div class="flex flex-wrap items-center gap-2 mt-0.5">
            <span class="text-xs md:text-sm text-slate-500 font-medium">{subject_tag} • 純國字大字體</span>
            <span class="bg-indigo-100 text-indigo-800 text-xs px-2.5 py-0.5 rounded-full font-black flex items-center gap-1">
              <span>🎙️</span> 微軟 Edge-TTS 臺灣真人語音
            </span>
          </div>
        </div>
      </div>
      
      <!-- 考生姓名與語音開關 -->
      <div class="flex items-center gap-3">
        <div class="flex items-center bg-blue-50 px-3 py-1.5 rounded-xl border border-blue-200 shadow-sm">
          <span class="text-sm font-black text-blue-900 mr-2">姓名：</span>
          <input id="student-name" type="text" placeholder="請輸入姓名" class="bg-white border border-blue-300 rounded px-2 py-0.5 text-sm w-28 focus:outline-none focus:ring-2 focus:ring-blue-500 font-bold" value="同學">
        </div>
        
        <button id="btn-auto-speak" onclick="toggleAutoSpeak()" class="flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all bg-emerald-600 text-white shadow hover:bg-emerald-700">
          <span id="auto-speak-icon">🔊</span>
          <span id="auto-speak-text">自動朗讀：開啟</span>
        </button>
      </div>
    </div>

    <!-- 進度條 -->
    <div class="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between gap-4">
      <div class="flex-1 bg-slate-100 rounded-full h-3.5 overflow-hidden border border-slate-200">
        <div id="progress-bar" class="bg-gradient-to-r from-blue-500 to-indigo-600 h-full rounded-full transition-all duration-300" style="width: 8.33%;"></div>
      </div>
      <div class="text-sm font-black text-blue-900 whitespace-nowrap">
        進度：<span id="current-q-num" class="text-xl text-blue-600 font-black">1</span> / <span id="total-q-num">12</span> 題
      </div>
    </div>
  </header>

  <!-- 試題主容器 -->
  <main id="exam-card-container" class="w-full max-w-4xl bg-white rounded-3xl shadow-lg border border-slate-200 p-5 md:p-8 flex-1 flex flex-col justify-between">
    <div id="question-content"></div>

    <!-- 底部導航與重聽功能 -->
    <footer class="mt-8 pt-4 border-t border-slate-200 flex flex-wrap items-center justify-between gap-4">
      <div class="flex items-center gap-3">
        <button id="btn-read-again" onclick="playCurrentQuestionAudio()" class="flex items-center gap-2 px-4 py-2.5 bg-amber-500 hover:bg-amber-600 text-white font-bold text-base rounded-2xl shadow transition transform active:scale-95">
          <span class="text-xl">📢</span> <span>重聽題目</span>
        </button>
        <button id="btn-read-slow" onclick="playCurrentQuestionAudio(0.75)" class="flex items-center gap-1.5 px-3.5 py-2 bg-amber-100 hover:bg-amber-200 text-amber-900 font-bold text-sm rounded-xl transition">
          <span>🐢</span> <span>慢速重聽</span>
        </button>
      </div>

      <div class="flex items-center gap-3">
        <button id="btn-prev" onclick="prevQuestion()" class="px-5 py-2.5 bg-slate-200 hover:bg-slate-300 text-slate-700 font-bold text-base rounded-2xl transition disabled:opacity-40 disabled:cursor-not-allowed">
          ⬅ 上一題
        </button>
        <button id="btn-next" onclick="nextQuestion()" class="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-bold text-lg rounded-2xl shadow-md transition transform active:scale-95 flex items-center gap-2">
          <span>下一題 ➡</span>
        </button>
      </div>
    </footer>
  </main>

  <!-- 結果結算畫面 -->
  <div id="result-modal" class="hidden w-full max-w-4xl bg-white rounded-3xl shadow-2xl border border-slate-200 p-6 md:p-10 my-4 text-center">
    <div class="text-6xl mb-3 animate-bounce">🏆</div>
    <h2 class="text-3xl font-black text-blue-900 mb-1">太棒了！測驗完成！</h2>
    <p class="text-slate-500 font-bold text-base mb-6">{exam_data.get("title", "")}</p>

    <div class="bg-gradient-to-br from-blue-50 to-indigo-50 border-2 border-blue-200 rounded-3xl p-6 mb-8 max-w-md mx-auto shadow-inner">
      <div class="text-sm font-bold text-blue-700 mb-1">考生：<span id="res-student-name" class="text-lg text-blue-900 font-black">同學</span></div>
      <div class="text-6xl font-black text-indigo-600 my-2" id="res-score">100 <span class="text-2xl font-bold text-slate-600">分</span></div>
      <div class="text-base font-bold text-emerald-700 flex items-center justify-center gap-2">
        <span>⭐ 表現優良！認字與聽理解能力非常優秀！</span>
      </div>
    </div>

    <div class="text-left mb-8">
      <h3 class="text-xl font-bold text-slate-800 mb-3 flex items-center gap-2">
        <span>📝</span> 逐題評量紀錄與 IEP 檢核對照表
      </h3>
      <div id="result-detail-list" class="space-y-2.5 max-h-80 overflow-y-auto pr-2"></div>
    </div>

    <div class="flex flex-wrap justify-center gap-4">
      <button onclick="restartExam()" class="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-bold text-lg rounded-2xl shadow transition transform active:scale-95">
        🔄 重新測驗一次
      </button>
      <button onclick="window.print()" class="px-6 py-3 bg-slate-700 hover:bg-slate-800 text-white font-bold text-lg rounded-2xl shadow transition transform active:scale-95">
        🖨️ 列印評量結果報告
      </button>
    </div>
  </div>

  <script>
    const EXAM_DATA = {json_data_str};
    const SYS_AUDIO = {sys_audio_str};
    let currentIndex = 0;
    let userAnswers = {{}};
    let isAutoSpeak = true;
    let currentAudioElem = null;

    function stopAllAudio() {{
      if (currentAudioElem) {{
        currentAudioElem.pause();
        currentAudioElem.currentTime = 0;
        currentAudioElem = null;
      }}
      if (window.speechSynthesis) {{
        window.speechSynthesis.cancel();
      }}
    }}

    function playAudioData(base64Data, playbackRate = 1.0, onEndCallback = null) {{
      stopAllAudio();
      if (!base64Data) return;
      const audio = new Audio(base64Data);
      audio.playbackRate = playbackRate;
      currentAudioElem = audio;
      audio.onended = () => {{
        currentAudioElem = null;
        if (onEndCallback) onEndCallback();
      }};
      audio.play().catch(e => console.log('Audio autoplay prevented or error:', e));
    }}

    function playChime(type = 'select') {{
      try {{
        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.connect(gain);
        gain.connect(ctx.destination);
        
        if (type === 'select') {{
          osc.frequency.setValueAtTime(587.33, ctx.currentTime);
          osc.frequency.exponentialRampToValueAtTime(880, ctx.currentTime + 0.12);
          gain.gain.setValueAtTime(0.15, ctx.currentTime);
          gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.12);
          osc.start();
          osc.stop(ctx.currentTime + 0.12);
        }}
      }} catch (e) {{}}
    }}

    function toggleAutoSpeak() {{
      isAutoSpeak = !isAutoSpeak;
      const btn = document.getElementById('btn-auto-speak');
      const icon = document.getElementById('auto-speak-icon');
      const txt = document.getElementById('auto-speak-text');
      if (isAutoSpeak) {{
        btn.className = "flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all bg-emerald-600 text-white shadow hover:bg-emerald-700";
        icon.innerText = "🔊";
        txt.innerText = "自動朗讀：開啟";
        if (SYS_AUDIO.auto_on) playAudioData(SYS_AUDIO.auto_on);
      }} else {{
        btn.className = "flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all bg-slate-400 text-white shadow hover:bg-slate-500";
        icon.innerText = "🔇";
        txt.innerText = "自動朗讀：關閉";
        stopAllAudio();
      }}
    }}

    function renderQuestion() {{
      stopAllAudio();
      const q = EXAM_DATA.questions[currentIndex];
      const total = EXAM_DATA.questions.length;
      
      document.getElementById('current-q-num').innerText = currentIndex + 1;
      document.getElementById('total-q-num').innerText = total;
      document.getElementById('progress-bar').style.width = `${{((currentIndex + 1) / total) * 100}}%`;
      document.getElementById('btn-prev').disabled = (currentIndex === 0);
      
      const isLast = (currentIndex === total - 1);
      const nextBtn = document.getElementById('btn-next');
      nextBtn.innerHTML = isLast ? '<span>看測驗結果 🏆</span>' : '<span>下一題 ➡</span>';
      nextBtn.className = isLast 
        ? "px-6 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-lg rounded-2xl shadow-md transition transform active:scale-95 flex items-center gap-2"
        : "px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-bold text-lg rounded-2xl shadow-md transition transform active:scale-95 flex items-center gap-2";

      const container = document.getElementById('question-content');
      container.innerHTML = '';

      const secHeader = document.createElement('div');
      secHeader.className = "flex items-center justify-between mb-4 pb-2 border-b-2 border-blue-100";
      secHeader.innerHTML = `
        <span class="text-sm md:text-base font-black text-blue-900 bg-blue-50 px-3.5 py-1 rounded-xl border border-blue-200">
          ${{q.section}}
        </span>
        <span class="text-sm font-black text-amber-800 bg-amber-50 px-3 py-1 rounded-lg border border-amber-200">
          ⭐ 本題 ${{q.score}} 分
        </span>
      `;
      container.appendChild(secHeader);

      if (q.type === 'match' || q.type === 'choice') {{
        renderStandardQuestion(q, container);
      }} else if (q.type === 'scenario') {{
        renderScenarioQuestion(q, container);
      }}

      if (isAutoSpeak) {{
        setTimeout(() => {{
          playCurrentQuestionAudio();
        }}, 250);
      }}
    }}

    function renderStandardQuestion(q, container) {{
      const card = document.createElement('div');
      card.className = "space-y-5";

      let imgHtml = '';
      if (q.img) {{
        imgHtml = `
          <div class="flex-shrink-0 text-center">
            <img src="${{q.img}}" alt="情境圖卡" class="w-36 h-36 md:w-44 md:h-44 object-contain rounded-2xl border-2 border-slate-200 bg-slate-50 p-2 shadow-sm inline-block">
          </div>
        `;
      }}

      const mainText = q.type === 'match' ? q.desc : q.q_text;

      card.innerHTML = `
        <div class="flex flex-col md:flex-row items-center gap-5 bg-gradient-to-r from-slate-50 to-blue-50/60 p-4 md:p-5 rounded-2xl border-2 border-slate-200 shadow-sm">
          ${{imgHtml}}
          <div class="flex-1 w-full">
            <div class="flex items-center gap-3 mb-2">
              <button onclick="playAudioData('${{q.audio_prompt}}')" class="px-3.5 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm md:text-base font-black rounded-xl shadow transition transform active:scale-95 flex items-center gap-1.5 flex-shrink-0">
                <span class="text-lg">🔊</span> <span>聽題目</span>
              </button>
              <span class="text-xs font-bold text-slate-500">點按鈕可隨時重聽題目</span>
            </div>
            <h3 class="text-xl md:text-2xl font-black text-slate-800 leading-snug tracking-wide">
              ${{mainText}}
            </h3>
            ${{q.type === 'match' ? '<p class="text-sm font-bold text-blue-700 mt-2">★ 請看圖片或點按鈕聽語音，點選最符合的卡片：</p>' : ''}}
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-3.5 pt-2" id="options-grid"></div>
      `;
      container.appendChild(card);

      const grid = container.querySelector('#options-grid');
      q.options.forEach(opt => {{
        const isSelected = (userAnswers[q.id] === opt.id);
        const cardBox = document.createElement('div');
        cardBox.className = `w-full p-3.5 md:p-4 rounded-2xl border-2 transition-all flex items-center justify-between gap-3 cursor-pointer ${{
          isSelected 
            ? 'card-selected border-blue-600 bg-blue-50 ring-2 ring-blue-400' 
            : 'border-slate-200 bg-white hover:border-blue-300 hover:bg-slate-50 shadow-sm'
        }}`;
        cardBox.onclick = () => selectOption(q.id, opt.id, opt.audio);

        cardBox.innerHTML = `
          <div class="flex items-center gap-3 flex-1">
            <span class="w-8 h-8 rounded-xl font-black flex items-center justify-center text-base flex-shrink-0 ${{
              isSelected ? 'bg-blue-600 text-white' : 'bg-slate-100 text-slate-700 border border-slate-200'
            }}">
              ${{opt.id}}
            </span>
            <div>
              <div class="text-lg md:text-xl font-black text-slate-800 leading-tight">${{opt.text}}</div>
              ${{opt.hint ? `<div class="text-xs md:text-sm text-slate-500 font-bold mt-0.5">${{opt.hint}}</div>` : ''}}
            </div>
          </div>

          <button onclick="event.stopPropagation(); playAudioData('${{opt.audio}}')" class="flex items-center gap-1 px-3 py-1.5 bg-indigo-50 hover:bg-indigo-100 text-indigo-800 border border-indigo-200 text-xs md:text-sm font-black rounded-xl shadow-sm transition transform active:scale-95 flex-shrink-0" title="點我聽這個選項發音">
            <span class="text-base">🔊</span>
            <span class="hidden sm:inline">聽選項</span>
          </button>
        `;
        grid.appendChild(cardBox);
      }});
    }}

    function renderScenarioQuestion(q, container) {{
      const card = document.createElement('div');
      card.className = "space-y-6";

      const contentLines = q.scenario_content.map(line => `<div class="py-0.5">${{line}}</div>`).join('');
      
      card.innerHTML = `
        <div class="bg-amber-50/70 border-2 border-amber-300 rounded-2xl p-4 md:p-5 shadow-sm">
          <div class="flex items-center justify-between mb-2">
            <h3 class="text-lg md:text-xl font-black text-amber-900 flex items-center gap-2">
              <span>📋</span> ${{q.scenario_title}}
            </h3>
            <button onclick="playAudioData('${{q.audio_scenario}}')" class="px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white font-black text-xs md:text-sm rounded-xl shadow transition transform active:scale-95 flex items-center gap-1.5 flex-shrink-0">
              <span class="text-base">🔊</span> <span>聽完整公告</span>
            </button>
          </div>
          <div class="text-sm md:text-base font-bold text-slate-800 bg-white/90 p-3.5 rounded-xl border border-amber-200 leading-relaxed shadow-inner">
            ${{contentLines}}
          </div>
        </div>

        <div class="space-y-5" id="sub-q-container"></div>
      `;
      container.appendChild(card);

      const subContainer = container.querySelector('#sub-q-container');
      q.sub_questions.forEach(sub => {{
        const subBox = document.createElement('div');
        subBox.className = "bg-slate-50 p-4 md:p-5 rounded-2xl border-2 border-slate-200 space-y-3 shadow-sm";
        
        subBox.innerHTML = `
          <div class="flex items-start gap-3">
            <button onclick="playAudioData('${{sub.audio}}')" class="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl shadow transition transform active:scale-95 flex items-center gap-1 flex-shrink-0">
              <span class="text-sm">🔊</span> <span class="text-xs font-black">聽題目</span>
            </button>
            <h4 class="text-base md:text-lg font-black text-slate-800 leading-snug">
              ${{sub.title}}
            </h4>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1" id="sub-opt-${{sub.sub_id}}"></div>
        `;
        subContainer.appendChild(subBox);

        const subOptGrid = subBox.querySelector(`#sub-opt-${{sub.sub_id}}`);
        sub.options.forEach(opt => {{
          const isSelected = (userAnswers[sub.sub_id] === opt.id);
          const optCard = document.createElement('div');
          optCard.className = `w-full p-3.5 rounded-xl border-2 transition-all flex items-center justify-between gap-2 cursor-pointer ${{
            isSelected 
              ? 'card-selected border-blue-600 bg-blue-50 shadow ring-2 ring-blue-400' 
              : 'border-slate-200 bg-white hover:border-blue-300'
          }}`;
          optCard.onclick = () => selectSubOption(sub.sub_id, opt.id, opt.audio);

          optCard.innerHTML = `
            <span class="text-base md:text-lg font-black text-slate-800 flex-1">${{opt.text}}</span>
            <button onclick="event.stopPropagation(); playAudioData('${{opt.audio}}')" class="flex items-center gap-1 px-2.5 py-1 bg-indigo-50 hover:bg-indigo-100 text-indigo-800 border border-indigo-200 text-xs font-black rounded-lg shadow-sm transition transform active:scale-95 flex-shrink-0">
              <span>🔊</span> <span>聽選項</span>
            </button>
          `;
          subOptGrid.appendChild(optCard);
        }});
      }});
    }}

    function selectOption(qId, optId, optAudio) {{
      userAnswers[qId] = optId;
      playChime('select');
      renderQuestion();
      if (optAudio) playAudioData(optAudio);
    }}

    function selectSubOption(subId, optId, optAudio) {{
      userAnswers[subId] = optId;
      playChime('select');
      renderQuestion();
      if (optAudio) playAudioData(optAudio);
    }}

    function playCurrentQuestionAudio(playbackRate = 1.0) {{
      const q = EXAM_DATA.questions[currentIndex];
      if (q.type === 'match' || q.type === 'choice') {{
        playAudioData(q.audio_prompt, playbackRate);
      }} else if (q.type === 'scenario') {{
        playAudioData(q.audio_scenario, playbackRate);
      }}
    }}

    function nextQuestion() {{
      if (currentIndex < EXAM_DATA.questions.length - 1) {{
        currentIndex++;
        renderQuestion();
      }} else {{
        showResult();
      }}
    }}

    function prevQuestion() {{
      if (currentIndex > 0) {{
        currentIndex--;
        renderQuestion();
      }}
    }}

    function showResult() {{
      stopAllAudio();
      if (SYS_AUDIO.finish_praise) playAudioData(SYS_AUDIO.finish_praise);

      document.getElementById('exam-card-container').classList.add('hidden');
      const modal = document.getElementById('result-modal');
      modal.classList.remove('hidden');

      const sName = document.getElementById('student-name').value || '同學';
      document.getElementById('res-student-name').innerText = sName;

      let totalScore = 0;
      const detailContainer = document.getElementById('result-detail-list');
      detailContainer.innerHTML = '';

      EXAM_DATA.questions.forEach((q, idx) => {{
        if (q.type === 'match' || q.type === 'choice') {{
          const isCorrect = (userAnswers[q.id] === q.correct);
          const earned = isCorrect ? q.score : 0;
          totalScore += earned;

          const row = document.createElement('div');
          row.className = `p-3.5 rounded-2xl border flex items-center justify-between gap-3 ${{
            isCorrect ? 'bg-emerald-50 border-emerald-200 text-emerald-900' : 'bg-rose-50 border-rose-200 text-rose-900'
          }}`;
          row.innerHTML = `
            <div class="flex items-center gap-3">
              <span class="text-xl font-black">${{isCorrect ? '✅' : '❌'}}</span>
              <div>
                <div class="font-black text-base">第 ${{idx + 1}} 題：${{q.type === 'match' ? q.desc : q.q_text}}</div>
                <div class="text-xs text-slate-600 mt-0.5">標準答案：【${{q.correct}}】 • 學生作答：【${{userAnswers[q.id] || '未作答'}}】</div>
              </div>
            </div>
            <div class="font-black text-base whitespace-nowrap">${{earned}} / ${{q.score}} 分</div>
          `;
          detailContainer.appendChild(row);
        }} else if (q.type === 'scenario') {{
          q.sub_questions.forEach((sub) => {{
            const isCorrect = (userAnswers[sub.sub_id] === sub.correct);
            const earned = isCorrect ? 5 : 0;
            totalScore += earned;

            const row = document.createElement('div');
            row.className = `p-3.5 rounded-2xl border flex items-center justify-between gap-3 ${{
              isCorrect ? 'bg-emerald-50 border-emerald-200 text-emerald-900' : 'bg-rose-50 border-rose-200 text-rose-900'
            }}`;
            row.innerHTML = `
              <div class="flex items-center gap-3">
                <span class="text-xl font-black">${{isCorrect ? '✅' : '❌'}}</span>
                <div>
                  <div class="font-black text-base">${{sub.title}}</div>
                  <div class="text-xs text-slate-600 mt-0.5">標準答案：【${{sub.correct}}】 • 學生作答：【${{userAnswers[sub.sub_id] || '未作答'}}】</div>
                </div>
              </div>
              <div class="font-black text-base whitespace-nowrap">${{earned}} / 5 分</div>
            `;
            detailContainer.appendChild(row);
          }});
        }}
      }});

      document.getElementById('res-score').innerHTML = `${{totalScore}} <span class="text-2xl font-bold text-slate-600">分</span>`;
    }}

    function restartExam() {{
      userAnswers = {{}};
      currentIndex = 0;
      document.getElementById('result-modal').classList.add('hidden');
      document.getElementById('exam-card-container').classList.remove('hidden');
      renderQuestion();
    }}

    window.addEventListener('DOMContentLoaded', () => renderQuestion());
  </script>
</body>
</html>
'''
