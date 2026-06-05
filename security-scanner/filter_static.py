import re
from mitmproxy import ctx, http
from mitmproxy.connection import Connection

class StaticResourceFilter:
    """
    Addon to filter out static resources and reduce unnecessary traffic.
    Supports both HTTP and HTTPS traffic through proxy tunneling.
    """
    
    def __init__(self):
        # 静态资源文件扩展名
        self.static_extensions = {
            'ico', 'jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'tiff',
            'css', 'js', 'woff', 'woff2', 'ttf', 'eot', 'otf', 'svg',
            'mp3', 'mp4', 'webm', 'wav', 'flac', 'aac',
            'pdf', 'doc', 'docx', 'xlsx', 'pptx', 'zip', 'tar', 'gz', 'rar',
            'exe', 'dll', 'so', 'dylib',
            'map', 'json'  # 也过滤source map和配置文件
        }
        
        # 静态资源路径关键字
        self.static_paths = [
            r'/fonts',
            r'/images',
            r'/img',
            r'/static',
            r'/assets',
            r'/media',
            r'/cdn',
            r'/js',
            r'/css',
            r'/vendor',
            r'/libs',
            r'/lib',
            r'/dist',
            r'/build',
            r'/public',
            r'/resources',
            r'/theme',
            r'/uploads',
            r'/download',
            r'/upload',
        ]
        
        self.blocked_count = 0
        self.allowed_count = 0
    
    def is_static_resource(self, url: str) -> bool:
 
        url_lower = url.lower()
        
        # 检查文件扩展名
        extension = url_lower.split('?')[0].split('#')[0].split('/')[-1].split('.')[-1]
        if extension and extension in self.static_extensions:
            return True
        
        # 检查路径中的静态资源目录
        for path_pattern in self.static_paths:
            if re.search(path_pattern, url_lower):
                return True
        
        # 特殊情况：排除数据URL
        if url_lower.startswith('data:'):
            return True
        
        return False
    
    def request(self, flow: http.HTTPFlow) -> None:
        """
        处理每个HTTP请求。
        如果是静态资源就直接拦截。
        
        Args:
            flow: HTTP流对象
        """
        url = flow.request.pretty_url
        
        if self.is_static_resource(url):
            self.blocked_count += 1
            ctx.log.info(f"[FILTERED] Blocking static: {url}")
            
            # 返回204 No Content 响应，节省带宽
            flow.response = http.Response.make(
                204,
                b'',
                {'Content-Type': 'text/plain'}
            )
        else:
            self.allowed_count += 1
            ctx.log.debug(f"[ALLOWED] Scanning: {url}")
    
    def tls_clienthello(self, data: bytes) -> None:
        """
        处理HTTPS TLS握手，允许任何HTTPS请求通过
        """
        ctx.log.debug("[HTTPS] TLS handshake initiated")
    
    def done(self) -> None:
        """
        扫描完成时的统计信息。
        """
        ctx.log.info(f"\n========================================")
        ctx.log.info(f"[STATISTICS] Static Resource Filter Summary")
        ctx.log.info(f"[STATISTICS] Blocked: {self.blocked_count} static resources")
        ctx.log.info(f"[STATISTICS] Allowed: {self.allowed_count} dynamic requests")
        ctx.log.info(f"[STATISTICS] Total: {self.blocked_count + self.allowed_count}")
        ctx.log.info(f"========================================")


addons = [StaticResourceFilter()]
