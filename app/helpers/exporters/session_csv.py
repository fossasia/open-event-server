from app.helpers.data_getter import DataGetter


class SessionCsv:

    @staticmethod
    def export(event_id):
        sessions = DataGetter.get_sessions_by_event_id(event_id)
        headers = 'Session Title, Session Speakers, \
            Session Track, Session Abstract, Email Sent'
        rows = [headers]
        for session in sessions:
            if not session.deleted_at:
                column = [session.title + ' (' + session.state + ')' if session.title else '']
                if session.speakers:
                    inSession = ''
                    for speaker in session.speakers:
                        if speaker.name:
                            inSession += (speaker.name + ', ')
                    column.append(inSession[:-2])
                column.append(session.track.name if session.track.name else '')
                column.append(strip_tags(session.short_abstract) if session.short_abstract else '')
                column.append('Yes' if session.state_email_sent else 'No')
                rows.append(','.join(column))

        csv_content = '\n'.join(rows)

        return csv_content
