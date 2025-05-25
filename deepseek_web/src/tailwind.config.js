// tailwind.config.js
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {},
    // 关键：确保container居中
    container: {
      center: true, // 启用容器居中
      padding: "1rem", // 可选：添加左右内边距避免贴边
    },
  },
  plugins: [],
};