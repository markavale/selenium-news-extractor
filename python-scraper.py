# from news_extractor.pipelines import StaticExtractorPipeline
from news_extractor.items import StaticArticleItem
from news_extractor.pipelines import StaticExtractorPipeline
# from news_extractor.items import StaticArticleItem
# from news_extractor.p
import scrapy
from pprint import pprint


pipeline_data = StaticExtractorPipeline()

meta_data = {
    "article_title": "Ultima hora de Pablo Iglesias y las elecciones en Madrid, en directo | Sanchez acusa al PP de corrupcion por alentar el transfuguismo",
    "article_source_url": "headtopics.com",
    "article_authors": [
        "1 hace horas"
    ],
    "article_sections": [],
    "article_publish_date": "2021-03-17T02:24:00.000Z",
    "article_content": "Sesiondecontrol, Isabel Diaz Ayuso Ultima hora de Pablo Iglesias y las elecciones en Madrid, en directo | Sanchez acusa al PP de corrupcion por alentar el transfuguismo El PP cree que las elecciones en Madrid seran el primer paso para la union del centro derecha | El Gobierno se somete a la primera sesion de control tras la salida de Iglesias 1 hace horas Fuente EL PAIS  TV en DIRECTO | Mientras Errejon pedia mas psicologos en la Sanidad Publica un diputado ha gritado 'vete al medico' y ha obligado a Batet a intervenir. El pleno ha acabado aplaudiendo la intervencion del portavoz de Mas Pais SesionDeControl El PP cree que las elecciones en Madrid seran el primer paso para la union del centro derecha | El Gobierno se somete a la primera sesion de control tras la salida de Iglesias \"Ustedes representan las malas artes, el transfuguismo, que es corrupcion\". Asi se ha dirigido el presidente del Gobierno, Pedro Sanchez, al lider del PP, Pablo Casado, este miercoles en la primera sesion de control despues de la renuncia del vicepresidente segundo, Pablo Iglesias, para concurrir como candidato de Unidas Podemos a las elecciones de la Comunidad de Madrid. Casado, por su parte, ha confiado en que los comicios seran el primer paso para la union del centro derecha: \"Espana es mucho mas que todos ustedes, y por eso el 4 de mayo ganara en Madrid la libertad\". En Murcia, la Asamblea regional debate hoy la mocion de censura impulsada por PSOE y Cs que desato la tormenta politica en otros territorios, especialmente en Madrid. El martes, Monica Garcia, candidata de Mas Madrid, rechazo concurrir a las elecciones autonomicas junto a Iglesias y su partido, Unidas Podemos. \"Poner tres opciones con posibilidad de arrebatarle a Ayuso la presidencia es lo mejor\", defendio por la noche en la cadena Ser. Garcia habia anunciado por la manana a traves de un video publicado en Twitter que su formacion no aceptaba Confinamientos de covid mejoraron calidad del aire en 84% de los paises Conductores de Uber con salario minimo, vacaciones y pension: como Reino Unido puede desatar una revolucion en la economia gig del mundo - BBC News Mundo \"Serian intocables\": el testimonio de un contador senala de vinculos con el narco al presidente de Honduras, Juan Orlando Hernandez - BBC News Mundo , mientras que Iglesias utilizo la misma red social para expresar el \"maximo respeto\" a la decision y prometer salir \"a por todo para frenar a los ultras\". Leer mas: EL PAIS >> Pablo Iglesias, candidato a las elecciones en Madrid, en directo | Pedro Sanchez, preguntado sobre Yolanda Diaz: \"Hay una vicepresidencia segunda que le corresponde a Unidas Podemos\" Casado y Ayuso aseguran que los comicios ahora decidiran entre \"comunismo y libertad\" | La presidenta madrilena: \"Espana me debe una. Hemos sacado a Iglesias de La Moncloa\" | Iglesias propone a Errejon \"una candidatura unica de izquierdas\" y plantea a Sanchez que Yolanda Diaz sea vicepresidenta segunda y Ione Belarra asuma el ministerio social Escribir Comentario Thank you for your comment. Please try again later. Ultimas Noticias Noticias 17 marzo 2021, miercoles Noticias Noticias anteriores Polemico divorcio entre Sebastien Loeb y Daniel Elena Siguiente noticia Noticias de ultima hora | Titulares | Espana Noticias - Head Topics",
    "article_images": [],
    "article_videos": [],
    "article_media_type": "web",
    "article_ad_value": 98640,
    "article_pr_value": 99626.4,
    "article_language": "en",
    "article_status": "Done",
    "collection_name": "article_link",
    "article_id": "",
    "article_error_status": None,
    "article_source_from": None,
    "date_created": "2021-03-17T11:13:51.953Z",
    "date_updated": "2021-03-17T11:13:51.953Z",
    "created_by": "Python Global Scraper",
    "updated_by": "Python Global Scraper",
    "is_in_mysql": True,
    "_id": "6051d840b5095b393dc89cf5",
    "website": {
        "alexa_rankings": {
            "global": 23339,
            "local": 40645
        },
        "website_cost": 300,
        "website_category": "News",
        "website_type": "INTERNATIONAL_NEWS",
        "country": "United States",
        "_id": "5f589551e87a173d70e8953c",
        "website_name": "Head Topics",
        "website_url": "http://headtopics.com",
        "fqdn": "headtopics.com"
    },
    "section": {
        "_id": "5f58a7a2e87a173d70e89b3e",
        "section_url": "http://headtopics.com/es"
    },
    "article_url": "http://headtopics.com/es/ltima-hora-de-pablo-iglesias-y-las-elecciones-en-madrid-en-directo-s-nchez-acusa-al-pp-de-corrup-19216907",
    "__v": 0
}


test_data = StaticExtractorPipeline()

pprint(test_data.process_item(meta_data, scrapy.Spider))