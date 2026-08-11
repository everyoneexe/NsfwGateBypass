function FindProxyForURL(url, host) {
  // Sadece Discord -> proxy
  if (host === "discord.com" ||
      host === "www.discord.com" ||
      dnsDomainIs(host, ".discord.com") ||
      dnsDomainIs(host, ".discordapp.com") ||
      dnsDomainIs(host, ".discord.gg") ||
      dnsDomainIs(host, ".discordapp.net")) {
    return "PROXY 127.0.0.1:8888";
  }
  // Geri kalan her sey direkt
  return "DIRECT";
}
