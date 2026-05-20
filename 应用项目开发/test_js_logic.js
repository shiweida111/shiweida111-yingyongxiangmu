// 模拟前端处理逻辑
const result = {
  prob_fake: 0.7188606848435996,
  norm_features: {
    "高频能量比": 0.2372809648513794,
    "纹理熵": 0.25326359514656194,
    "局部二值模式": 0.0001359756586477321,
    "噪声残差比": 1.0,
    "拉普拉斯方差": 1.0,
    "饱和度方差": 0.31964417546987534,
    "亮度方差": 0.3725814074277878
  }
};

// 测试 isNaN 和 typeof
console.log("=== 测试 isNaN 和 typeof ===");
console.log(`prob_fake: ${result.prob_fake}`);
console.log(`typeof prob_fake: ${typeof result.prob_fake}`);
console.log(`isNaN(prob_fake): ${isNaN(result.prob_fake)}`);
console.log(`!isFinite(prob_fake): ${!isFinite(result.prob_fake)}`);

// 测试遍历对象
console.log("\n=== 测试遍历对象 ===");
for (const key in result.norm_features) {
  const value = result.norm_features[key];
  console.log(`${key}: ${value}`);
  console.log(`  typeof: ${typeof value}`);
  console.log(`  parseFloat: ${parseFloat(value)}`);
  console.log(`  isNaN(parseFloat(value)): ${isNaN(parseFloat(value))}`);
}

// 测试转换为数组
console.log("\n=== 测试转换为数组 ===");
const featureArray = [];
for (const key in result.norm_features) {
  const value = parseFloat(result.norm_features[key]);
  const normalizedValue = isNaN(value) || !isFinite(value) ? 0 : value;
  featureArray.push({
    name: key,
    value: normalizedValue
  });
}

console.log("转换后的数组:");
for (const item of featureArray) {
  console.log(`${item.name}: ${(item.value * 100).toFixed(2)}%`);
}