
# 📘 Skyhigh Secure Web Gateway 정책 구조 설명 (Prompt용)

이 문서는 Skyhigh SWG의 JSON 정책 응답 구조를 모델이 **정확하게 이해하고 처리할 수 있도록** 정리한 문서입니다.

모델은 이 구조 설명을 참고하여 JSON 구조를 해석하거나 설명하는 데 활용해야 합니다.  
**실제 파싱 또는 코드 작성은 요구되지 않으며, 구조 이해와 설명 용도로만 사용합니다.**

---

## ✅ 구조 요약 형식

구조는 아래와 같이 정리되어 있습니다:

```
keyName [type1, type2, ...]: subkey1, subkey2, ...
```

- `keyName`: JSON 내에서 사용되는 키 이름
- `typeX`: 해당 key에 나타날 수 있는 값의 타입 (예: `dict`, `list<dict>`, `str`, `null` 등)
- `subkeyX`: 값이 `dict` 또는 `list<dict>`일 경우 그 내부에 존재하는 하위 key 목록

---

## ✅ 모델이 이해해야 할 주요 포인트

- 하나의 key는 **여러 타입(type)**으로 등장할 수 있음
- 일부 key는 **자기 자신을 포함하는 중첩 구조**임 (재귀 구조)
- 일부 key는 **nullable 구조** (`null`이 값으로 존재할 수 있음)
- `list<dict>`는 리스트 안에 dict들이 있다는 의미임
- sub-keys는 해당 key의 값이 dict이거나 dict 리스트일 때 존재하는 하위 항목임
- **형식은 단순하지만 의미는 트리 구조를 내포**하고 있음

---

## 🔁 재귀/중첩 구조 주의

다음 key들은 자기 자신 또는 유사한 구조를 여러 단계 중첩하여 포함할 수 있습니다:

- `ruleGroup` → 하위에 또 다른 `ruleGroup` 포함
- `entry` → 하위에 `list` → `listEntry` → 또 `entry` 구조 반복
- `parameter` → 내부 `value` → 내부 `propertyInstance` → 다시 `parameter` 포함

이러한 구조는 **중첩 깊이가 깊어질 수 있음**을 의미합니다.

---

## ⚠️ 타입이 복잡하거나 혼합된 키

아래 key들은 단일 타입이 아닌, 여러 형태로 등장하는 대표적인 예입니다:

| key        | type 종류                                 |
|------------|--------------------------------------------|
| `entry`    | dict, list, list<dict>, str               |
| `ruleGroup`| dict, list<dict>                          |
| `expressions` | dict, null                             |
| `rules`    | dict, null                                |
| `configurationProperty` | list, list<dict>             |

모델은 이 경우 타입에 따라 구조가 달라질 수 있다는 점을 인식해야 합니다.

---

## 🧠 모델이 할 수 있는 일 (이 문서를 기반으로)

- 각 key의 구조를 설명하거나 시각화 요청에 응답
- 중복 구조 여부나 중첩 패턴 설명
- 특정 key의 value가 어떤 구조인지 추론
- `ruleGroup` 안에 또 `ruleGroup`이 있는지 등 확인
- 잘못된 구조 또는 불일치 탐지 가능성 판단

---

## 📌 구조 요약 데이터 (붙여넣기됨)

> 구조 요약은 key와 타입, 하위 키 정보를 포함하고 있으며, 다음 섹션을 참고하여 인식하세요.

<details>
<summary>클릭하여 전체 구조 펼치기</summary>

```
libraryContent [dict]: configurations, libraryObject, lists, ruleGroup
libraryObject [dict]: description, name, version
name [str]:
version [str]:
description [null, str]:
lists [dict]: entry
entry [dict, list, list<dict>, str]: list, parameter, string
string [str]:
list [dict]: @classifier, @defaultRights, @feature, @id, @mwg-version, @name, @structuralList, @subId, @systemList, @typeId, @version, content, description, setup
@version [str]:
@mwg-version [str]:
@name [str]:
@id [str]:
@typeId [str]:
@classifier [str]:
@systemList [str]:
@structuralList [str]:
@defaultRights [str]:
content [dict, null]: listEntry
listEntry [dict, list, list<dict>]: complexEntry, description, entry
complexEntry [dict]: @defaultRights, acElements, configurationProperties
configurationProperties [dict]: configurationProperty
configurationProperty [list, list<dict>]: @encrypted, @key, @listType, @type, @value
@key [str]:
@type [str]:
@encrypted [str]:
@value [str]:
@listType [str]:
@feature [str]:
setup [dict]: connection, proxy, updateTime
connection [dict]: credentials, url
url [str]:
credentials [dict]: password, username
username [null, str]:
password [null, str]:
proxy [dict]: credentials, host, port
host [null]:
port [null]:
updateTime [dict]: hourly
hourly [dict]: @minute
@minute [str]:
acElements [null]:
@subId [str]:
configurations [dict]: configuration
configuration [list, list<dict>]: @defaultRights, @id, @mwg-version, @name, @targetId, @templateId, @version, acElements, configurationProperties, description
@templateId [str]:
@targetId [str]:
ruleGroup [dict, list, list<dict>]: @cloudSynced, @cycleEmbeddedObject, @cycleRequest, @cycleResponse, @defaultRights, @enabled, @id, @name, acElements, condition, description, ruleGroups, rules
@enabled [str]:
@cycleRequest [str]:
@cycleResponse [str]:
@cycleEmbeddedObject [str]:
@cloudSynced [str]:
condition [dict]: @always, expressions
@always [str]:
expressions [dict, null]: conditionExpression, setExpression
conditionExpression [dict, list, list<dict>]: @closingBracketCount, @openingBracketCount, @operatorId, @prefix, parameter, propertyInstance
@openingBracketCount [str]:
@closingBracketCount [str]:
@operatorId [str]:
propertyInstance [dict]: @configurationId, @propertyId, @useMostRecentConfiguration, parameters
@useMostRecentConfiguration [str]:
@propertyId [str]:
parameter [dict]: @listTypeId, @typeId, @valueId, @valueTyp, value
@valueTyp [str]:
@listTypeId [str]:
@value [dict]: listValue, propertyInstance, stringValue
listValue [dict]: @id
rules [dict, null]: rule
ruleGroups [dict, null]: ruleGroup
rule [dict, list, list<dict>]: @enabled, @id, @name, actionContainer, condition, description, immediateActionContainers
immediateActionContainers [dict, null]: enableEngineActionContainer, executeActionContainer, setActionContainer
executeActionContainer [dict, list, list<dict>]: procedureValue
procedureValue [dict]: @procedureId, parameters
@procedureId [str]:
parameters [dict, null]: entry
stringValue [dict]: @stringModifier, @typeId, @value
@stringModifier [str]:
actionContainer [dict]: @actionId, @configurationId
@actionId [str]:
@valueId [str]:
@configurationId [str]:
@prefix [str]:
enableEngineActionContainer [dict]: @configurationId, @engineId
@engineId [str]:
setActionContainer [dict, list, list<dict>]: @propertyId, expressions
setExpression [dict]: @closingBracketCount, @openingBracketCount, parameter
```

</details>

---

## ✅ 요약

이 문서의 목적은 모델이 **Skyhigh SWG 정책 JSON 구조를 정확히 이해**하고,  
**구조 설명, 구조 시각화, 키 관계 해석 등 구조적 판단에 활용**하는 것입니다.

이 문서에 정의된 규칙과 예시를 기반으로, **실제 JSON 파일이 주어졌을 때 구조를 설명하거나 정리된 요약을 제공**할 수 있어야 합니다.
