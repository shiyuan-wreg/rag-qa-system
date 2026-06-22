export default function Learn() {
  // 学习站点由 Nginx 静态托管于 /learn，这里直接跳转
  if (typeof window !== 'undefined') window.location.href = '/learn/'
  return null
}
