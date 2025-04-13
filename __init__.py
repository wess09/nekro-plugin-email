from email.message import EmailMessage
import smtplib
from nekro_agent.api.schemas import AgentCtx
from nekro_agent.core import logger
from nekro_agent.services.plugin.base import ConfigBase, NekroPlugin, SandboxMethodType
from pydantic import Field

# TODO: 插件元信息，请修改为你的插件信息
plugin = NekroPlugin(
    name="电子邮件",  # TODO: 插件名称
    module_name="nekro_plugin_email",  # TODO: 插件模块名 (如果要发布该插件，需要在 NekroAI 社区中唯一)
    description="给与 AI 发送邮件的能力",  # TODO: 插件描述
    version="0.1.4",  # TODO: 插件版本
    author="wess09",  # TODO: 插件作者
    url="https://github.com/wess09/nekro-plugin-email",  # TODO: 插件仓库地址
)


# TODO: 插件配置，根据需要修改
@plugin.mount_config()
class EmailConfig(ConfigBase):
    """电子邮件配置"""

    SMTP_SERVER: str = Field(
        default="smtp.example.com",
        title="SMTP服务器地址",
        description="发件邮箱的SMTP服务器地址",
    )
    SMTP_PORT: int = Field(
        default=587,
        title="SMTP端口",
        description="SMTP服务器的连接端口",
    )
    USERNAME: str = Field(
        default="your_email@example.com",
        title="邮箱账号",
        description="发件人的邮箱地址",
    )
    PASSWORD: str = Field(
        default="your_password",
        title="邮箱密码",
        description="发件邮箱的授权密码",
    )
    USE_TLS: bool = Field(
        default=True,
        title="启用TLS",
        description="是否使用TLS安全连接",
    )


# 获取配置实例
config: EmailConfig = plugin.get_config(EmailConfig)


@plugin.mount_sandbox_method(SandboxMethodType.AGENT, name="发送邮件", description="通过SMTP协议发送电子邮件")
async def send_email(_ctx: AgentCtx, to_addr: str, subject: str, body: str) -> str:
    """发送电子邮件到指定地址。

    Args:
        to_addr: 收件人邮箱地址
        subject: 邮件主题
        body: 邮件正文内容

    Returns:
        str: 发送成功返回'success'，失败返回错误信息

    Example:
        发送测试邮件:
        send_email(to_addr="recipient@example.com", subject="测试邮件", body="这是一封测试邮件")
    """

    msg = EmailMessage()
    msg['From'] = config.USERNAME
    msg['To'] = to_addr
    msg['Subject'] = subject
    msg.set_content(body)

    try:
        with smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT) as server:
            if config.USE_TLS:
                server.starttls()
            server.login(config.USERNAME, config.PASSWORD)
            server.send_message(msg)
            logger.info(f"成功发送邮件到 {to_addr}")
            return "success"
    except smtplib.SMTPException as e:
        logger.error(f"邮件发送失败: {str(e)}")
        return f"邮件发送失败: {str(e)}"
    except Exception as e:
        logger.exception(f"发送邮件时发生意外错误: {e}")
        return f"发送邮件时发生系统错误: {str(e)}"


@plugin.mount_cleanup_method()
async def clean_up():
    """清理SMTP连接"""
    # SMTP连接在with语句中自动管理，此处无需额外清理
    logger.info("邮件插件资源已清理")
