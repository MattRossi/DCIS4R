from datetime import datetime
from Organization import Orgs

class Webhook:
    icon_url = {
        Orgs.DCI: "https://i.imgur.com/GQs6PdZ.png",
        Orgs.DCA: "https://dcacorps.org/wp-content/uploads/2021/01/DCA_Logo-Blue-e1611100552664.png"
    }

    color = {
        Orgs.DCI: 13810806,
        Orgs.DCA: 87462
    }

    def generate_schedule(show, org):
        sched = ''
        if org == Orgs.DCI:
            for p in show.lineup:
                sched = sched + '{} - {}\n'.format(p.time, ('**' + p.corps + '**' + ((' - *' + p.location + '*') if p.location else '')))
        elif org == Orgs.DCA:
            for p in show.lineup:
                sched = sched + '{}\n'.format(p)
        return sched

    def embedBuilder(show, org):
        author = {
            "name": show.name, # show name
            "url": show.url, # show page
            "icon_url": Webhook.icon_url.get(org) #org logo
        }
        footer = {
            "text": "All times {} and subject to change".format(show.timezone)
        }
        image = {
            "url": show.image # image URL
        }
        if org == Orgs.DCI:
            start = show.full_date
        elif org == Orgs.DCA:
            start = '{} {}'.format(datetime.strptime("{} {}".format(show.date, show.start_time), '%Y-%m-%d %I:%M %p').strftime('%A, %d %b %Y %I:%M %p'), show.timezone)
        start_time = {
            "name": "Start Time",
            "value": start # start time
        }
        schedule = {
            "name": "Schedule",
            "value": Webhook.generate_schedule(show, org) #formatted schedule
        }
        streaming = {
            "name": "Watch Live on FloMarching",
            "value": show.streaming
        }
        embed = {
            "title": show.location, # show location
            "color": Webhook.color.get(org),
            "fields": [ start_time, schedule, streaming ] if show.streaming else [ start_time, schedule ],
            "author": author,
            "footer": footer,
            "image": image
        }
        complete = {
            "content": None,
            "embeds": [embed],
            "attachments": []
        }
        print(complete)
        return complete