// Disease treatment database
const treatmentDatabase = {
'Healthy-leaf': {
classification: 'classification-healthy',
treatment: [
'ต้นมะม่วงของคุณมีสุขภาพดี',
'รดน้ำสม่ำเสมอแต่อย่าให้ขัง',
'ใส่ปุ๋ยอินทรีย์ทุก 2-3 เดือน',
'ตัดแต่งกิ่งที่แห้งหรือตายออก',
'ตรวจเช็คศัตรูพืชเป็นประจำ'
]
},
'Healthy-Fruit': {
classification: 'classification-healthy',
treatment: [
'ผลมะม่วงของคุณมีสุขภาพดี',
'เก็บเกี่ยวเมื่อสุกเต็มที่',
'เก็บรักษาในที่เย็นและแห้ง',
'หลีกเลี่ยงการกระแทกหรือบอบช้ำ'
]
},
'Anthracnose-leaf': {
classification: 'classification-disease',
treatment: [
'ตัดใบที่เป็นโรคทิ้งและเผาทำลาย',
'ใช้สารเคมีป้องกันกำจัดเชื้อรา เช่น คาร์เบนดาซิม หรือ โพรพิโคนาโซล',
'พ่นสารป้องกันทุก 7-10 วัน ในช่วงฝนตก',
'ปรับปรุงการระบายน้ำในแปลง',
'ลดความชื้นรอบต้นไม้'
]
},
'Anthracnose-Fruit': {
classification: 'classification-disease',
treatment: [
'เก็บผลที่เป็นโรคทิ้ง',
'พ่นสารป้องกันเชื้อราหลังดอกบาน',
'ใช้สารเคมี เช่น แมนโคเซบ หรือ คลอโรธาโลนิล',
'เก็บเกี่ยวผลผลิตทันเวลา',
'หลีกเลี่ยงการเก็บเกี่ยวในช่วงฝนตก'
]
},
'Alternaria-Fruit': {
classification: 'classification-disease',
treatment: [
'ตัดผลที่เป็นโรคทิ้ง',
'ใช้สารป้องกันเชื้อรา เช่น ไดฟีโนโคนาโซล',
'รักษาความสะอาดในสวน',
'หลีกเลี่ยงการบาดเจ็บของผลไม้'
]
},
'Black Mould Rot-Fruit': {
classification: 'classification-disease',
treatment: [
'ตัดผลที่เป็นโรคทิ้ง',
'ลดความชื้นในสวน',
'ใช้สารป้องกันเชื้อรา',
'ปรับปรุงการระบายอากาศ',
'เก็บเกี่ยวผลผลิตทันเวลา'
]
},
'Stem end Rot-Fruit': {
classification: 'classification-disease',
treatment: [
'ตัดผลที่เป็นโรคทิ้ง',
'ใช้สารป้องกันเชื้อรา',
'เก็บเกี่ยวอย่างระมัดระวัง',
'เก็บรักษาในที่เย็นและแห้ง'
]
},
'Bacterial Canker-leaf': {
classification: 'classification-disease',
treatment: [
'ตัดใบที่เป็นโรคทิ้งและเผาทำลาย',
'ใช้สารป้องกันแบคทีเรีย เช่น คอปเปอร์',
'หลีกเลี่ยงการบาดเจ็บของต้นไม้',
'ปรับปรุงการระบายน้ำ'
]
},
'Cutting Weevil-leaf': {
classification: 'classification-pest',
treatment: [
'ใช้กับดักแมลง',
'ใช้สารกำจัดแมลง เช่น ไพรีทริน',
'เก็บตัวอ่อนและตัวเต็มวัยออก',
'รักษาความสะอาดในสวน'
]
},
'Die Back-leaf': {
classification: 'classification-disease',
treatment: [
'ตัดกิ่งที่แห้งทิ้ง',
'ใช้สารป้องกันเชื้อรา',
'ใส่ปุ๋ยเสริมความแข็งแรง',
'รดน้ำอย่างเพียงพอ'
]
},
'Gall Midge-leaf': {
classification: 'classification-pest',
treatment: [
'ตัดใบที่เป็นโรคทิ้ง',
'ใช้สารกำจัดแมลง เช่น อิมิดาโคลพริด',
'ใช้กับดักสีเหลือง',
'รักษาความสะอาดในสวน'
]
},
'Powdery Mildew-leaf': {
classification: 'classification-disease',
treatment: [
'ตัดใบที่เป็นโรคทิ้ง',
'ใช้สารป้องกันเชื้อรา เช่น ไตรฟอรีน',
'ปรับปรุงการระบายอากาศ',
'ลดความชื้นรอบต้นไม้'
]
},
'Sooty Mould-leaf': {
classification: 'classification-disease',
treatment: [
'ควบคุมแมลงปากดูด เช่น เพลี้ยแป้ง',
'ใช้สารล้างน้ำมันแร่',
'ล้างใบด้วยน้ำสบู่',
'ปรับปรุงการระบายอากาศ'
]
}
};

