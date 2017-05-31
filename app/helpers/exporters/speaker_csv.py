from app.helpers.data_getter import DataGetter


class SpeakerCsv:

    @staticmethod
    def export(event_id):
        speakers = DataGetter.get_speakers(event_id)
        headers = 'Speaker Name, Speaker Email, Speaker Session(s), \
                Speaker Mobile, Speaker Organisation, Speaker Position'
        rows = [headers]
        for speaker in speakers:
            column = [speaker.name if speaker.name else '', speaker.email if speaker.email else '']
            if speaker.sessions:
                session_details = ''
                for session in speaker.sessions:
                    if not session.deleted_at:
                        session_details += session.title + ' (' + session.state + '), '
                column.append(session_details[: -2])
            column.append(speaker.mobile if speaker.mobile else '')
            column.append(speaker.organisation if speaker.organisation else '')
            column.append(speaker.position if speaker.position else '')
            rows.append(','.join(column))

        csv_content = '\n'.join(rows)

        return csv_content
