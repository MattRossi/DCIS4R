import platform

class PostFormatter:
    def create_header(show, org):
        body = ''
        body = body + '[**{} {} Page**]({})'.format(show.name, org, show.url)
        body = body + '\n\n'
        return body

    def create_post_footer(body):
        body = body + '## Join our [Discord server](https://discord.gg/drumcorps) for real-time discussion with other drum corps fans and marching members!'
        return body

    def create_title(parsed_shows, org, today):
        print('Running on ' + platform.system())
        if 'Win' in platform.system():
            title_date_format = '%#m/%#d'
        else:
            title_date_format = '%-m/%-d'
        title = '[{} Show Thread] '.format(org.name)
        title = title + today.strftime(title_date_format) + ': '
        if org.name == 'DCI':
            title = title + ' | '.join([str(x.name + ' - ' + x.location) for x in parsed_shows])
        elif org.name == 'DCA':
            title = title + ' | '.join([str(x.name) for x in parsed_shows])
        return title
