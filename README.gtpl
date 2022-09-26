<div align="center">
<img src="https://github-readme-stats.vercel.app/api?username=ChrisTitusTech&show_icons=true&theme=tokyonight">
<table><tr>
  <td><img src="https://wakatime.com/share/@christitustech/4c17a227-eb23-48c5-a2f1-492e5538842c.svg"</td>
  <td><img src="https://wakatime.com/share/@christitustech/57160975-2111-472e-bc92-f390b42053b3.svg"</td>
</tr><tr>
  <td><img src="https://wakatime.com/share/@christitustech/b7d6c245-11dd-4802-a2dd-8ff0fd915324.svg"</td>
  <td><img src="https://wakatime.com/share/@christitustech/29475f0b-8d50-47b4-aaf5-f96bdcab9d0d.svg"</td>
</tr></table>
</div>
### 👷 Check out what I'm currently working on
{{ range recentContributions 5 }}
- [{{ .Repo.Name }}]({{ .Repo.URL }}) - {{ .Repo.Description }}
{{- end }}
### 🌱 My latest projects
{{ range recentRepos 5 }}
- [{{ .Name }}]({{ .URL }}) - {{ .Description }}
{{- end }}
### 🔨 My recent Pull Requests
{{ range recentPullRequests 5 }}
- [{{ .Title }}]({{ .URL }}) on [{{ .Repo.Name }}]({{ .Repo.URL }})
{{- end }}
### ⭐ Recent Stars
{{ range recentStars 5 }}
- [{{ .Repo.Name }}]({{ .Repo.URL }}) - {{ .Repo.Description }}
{{- end }}
### 📰 Recent Blog Posts
{{ range rss "https://christitus.com/index.xml" 5 }}
- [{{ .Title }}]({{ .URL }})
{{- end }}
### 📫 How to reach me:
  - Youtube   : <https://youtube.com/c/ChrisTitusTech>
  - Twitch    : <https://twitch.tv/christitustech>
  - Twitter   : <https://twitter.com/christitustech>
  - Website   : <https://christitus.com>
  - Web Store : <https://cttstore.com>
