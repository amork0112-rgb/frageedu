// src/components/EntranceStepper.jsx
import React, { useMemo } from "react";

// brchType: kinder | junior | middle
// flowType: transfer | regular  (kinder 전용)
const makeSteps = (brchType, flowType) => {
  const isTestTrack = brchType === "junior" || brchType === "middle";

  // KINDER 분기: 편입 vs 정규입학
  if (brchType === "kinder") {
    if (flowType === "regular") {
      // 프라게 킨더 정규입학
      return [
        { key: "seminar",  title: "01. 설명회",               desc: "학부모 대상 설명회 참석으로 교육 철학·프로그램을 이해합니다." },
        { key: "forms",    title: "02. 입학원서 작성",        desc: "온라인 입학원서를 제출합니다." },
        { key: "newcomer", title: "03. 신입생 안내 및 동의서", desc: "신입생 안내(교재 주문·셔틀 등)와 필수 동의 절차를 완료합니다." },
      ];
    }
    // default: transfer (편입)
    return [
      { key: "welcome",   title: "01. 안내 확인",                        desc: "프로그램·시간표·수업 안내를 확인합니다." },
      { key: "consult",   title: "02. 상담 및 테스트 신청",              desc: "상담 예약 후 필요 시 간단한 테스트를 진행합니다." },
      { key: "forms",     title: "03. 원서 제출",                        desc: "학생 등록 카드·기초 실태·우유·방과후 신청서를 작성합니다." },
      { key: "placement", title: "04. 반 배정 상담",                     desc: "연령/학년/요일을 고려해 배정 상담을 진행합니다." },
      { key: "enroll",    title: "05. 수강료 납입 · 신입생 안내",        desc: "첫 달 수강료 납입 후 신입생 안내(교재·셔틀 등, 이후 동의서/안내 발송)." },
    ];
  }

  // JUNIOR / MIDDLE (입학시험 필수)
  if (isTestTrack) {
    return [
      { key: "welcome",  title: "01. 안내 확인",                   desc: "프로그램·시간표·수업 안내를 확인합니다." },
      { key: "reserve",  title: "02. 입학시험 예약",               desc: "홈페이지 로그인 후 안내된 응시 가능 일정 중 선택·예약합니다." },
      { key: "exam",     title: "03. 입학시험 응시",               desc: "모든 응시는 오프라인으로 진행됩니다." },
      { key: "result",   title: "04. 입학 결과 상담",             desc: "시험 결과 기반 단계·프로그램 상담, 요일/학년 고려 반 선택." },
      { key: "enroll",   title: "05. 수강료 납입 · 신입생 안내",   desc: "첫 달 수강료 납입 후 신입생 안내(교재·셔틀, 이후 동의서/안내 발송)." },
    ];
  }

  // fallback
  return [];
};

export default function EntranceStepper({
  step = 1,
  brchType = "kinder",
  flowType = "transfer", // kinder 전용: 'transfer' | 'regular'
  token,
}) {
  const steps = useMemo(() => makeSteps(brchType, flowType), [brchType, flowType]);

  // 과정명 표기
  const courseLabel =
    brchType === "kinder"
      ? `프라게 킨더 · ${flowType === "regular" ? "정규입학" : "편입"}`
      : brchType === "junior"
      ? "프라게 주니어"
      : "프라디스 중등";

  return (
    <section className="py-14 bg-gradient-to-br from-purple-50 to-indigo-50">
      <div className="max-w-5xl mx-auto px-4">
        {/* 헤더 */}
        <div className="mb-10 text-center">
          <h1 className="text-3xl lg:text-5xl font-bold tracking-tight">프라게 입학 절차</h1>
          <p className="text-gray-600 mt-3">과정: <span className="font-medium">{courseLabel}</span></p>
        </div>

        {/* 스텝 카드 */}
        <ol className={`grid gap-3 ${steps.length <= 3 ? "md:grid-cols-3" : "md:grid-cols-5"} grid-cols-1`}>
          {steps.map((s, idx) => {
            const num = idx + 1;
            const active = num === step;
            const done = num < step;
            const tone = active ? "border-purple-500" : done ? "border-green-400" : "border-gray-200";
            return (
              <li key={s.key} className={`rounded-xl p-4 border bg-white shadow-sm ${tone}`}>
                <div className="flex items-center gap-2 mb-2">
                  <span className={`text-sm px-2 py-0.5 rounded
                    ${active ? "bg-purple-100 text-purple-700"
                             : done   ? "bg-green-100 text-green-700"
                                      : "bg-gray-100 text-gray-600"}`}>
                    {String(num).padStart(2, "0")}
                  </span>
                  <h3 className="font-semibold">{s.title}</h3>
                </div>
                <p className="text-sm text-gray-600">{s.desc}</p>

                {/* CTA: 스텝별 행동 */}
                {active && (
                  <div className="mt-4 flex flex-wrap gap-2">
                    {s.key === "seminar" && (
                      <a href={`/kinder/seminar`} className="px-3 py-2 rounded-lg bg-purple-600 text-white text-sm">설명회 신청</a>
                    )}
                    {s.key === "consult" && (
                      <a href={`/consult?brchType=kinder`} className="px-3 py-2 rounded-lg bg-purple-600 text-white text-sm">상담 예약</a>
                    )}
                    {s.key === "forms" && (
                      <a href={`/form?id=${token || ""}`} className="px-3 py-2 rounded-lg border text-sm">원서 작성</a>
                    )}
                    {s.key === "placement" && (
                      <a href={`/consult/placement?brchType=kinder`} className="px-3 py-2 rounded-lg border text-sm">배정 상담 예약</a>
                    )}
                    {s.key === "reserve" && (
                      <a href={`/exam/reserve?brchType=${brchType}`} className="px-3 py-2 rounded-lg bg-purple-600 text-white text-sm">입학시험 예약</a>
                    )}
                    {s.key === "exam" && (
                      <a href={`/exam/guide?brchType=${brchType}`} className="px-3 py-2 rounded-lg border text-sm">시험 안내 보기</a>
                    )}
                    {s.key === "result" && (
                      <a href={`/consult/result?brchType=${brchType}`} className="px-3 py-2 rounded-lg border text-sm">결과 상담 예약</a>
                    )}
                    {s.key === "enroll" && (
                      <a href={`/newcomer?brchType=${brchType}`} className="px-3 py-2 rounded-lg border text-sm">신입생 안내</a>
                    )}
                  </div>
                )}
              </li>
            );
          })}
        </ol>

        {/* 이전/다음 */}
        <div className="mt-10 flex justify-between">
          <a
            href={`/entrance/step?brchType=${brchType}&flowType=${flowType}&step=${Math.max(1, step - 1)}${token ? `&id=${token}` : ""}`}
            className="text-sm text-gray-600 hover:text-gray-900"
          >
            ← 이전
          </a>
          <a
            href={`/entrance/step?brchType=${brchType}&flowType=${flowType}&step=${Math.min(steps.length, step + 1)}${token ? `&id=${token}` : ""}`}
            className="text-sm text-purple-700 hover:text-purple-900"
          >
            다음 →
          </a>
        </div>
      </div>
    </section>
  );
}
