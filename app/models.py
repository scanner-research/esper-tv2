from esperlib.models import EsperModel, Video, Frame, CharField, Track, Pose, BoundingBox, FK, Features

from django.db import models
import math
import numpy as np
import tempfile
import subprocess as sp


class IdentityTag(EsperModel):
    name = CharField(unique=True)


class Identity(EsperModel):
    name = CharField(unique=True)
    tags = models.ManyToManyField(IdentityTag, blank=True)


class CanonicalShow(EsperModel):
    name = CharField(unique=True)
    is_recurring = models.BooleanField(default=False)
    hosts = models.ManyToManyField(Identity, blank=True)


class Show(EsperModel):
    name = CharField(unique=True)
    hosts = models.ManyToManyField(Identity, blank=True)
    canonical_show = FK(CanonicalShow)


class Channel(EsperModel):
    name = CharField(unique=True)


class Video(Video):
    channel = FK(Channel)
    show = FK(Show)
    time = models.DateTimeField()
    commercials_labeled = models.BooleanField(default=False)
    srt_extension = CharField()
    threeyears_dataset = models.BooleanField(default=False)
    duplicate = models.BooleanField(default=False)
    corrupted = models.BooleanField(default=False)

    def get_stride(self):
        return int(math.ceil(self.fps) / 2)

    def item_name(self):
        return '.'.join(self.path.split('/')[-1].split('.')[:-1])

    def url(self, duration='1d'):
        fetch_cmd = 'PYTHONPATH=/usr/local/lib/python2.7/dist-packages:$PYTHONPATH gsutil signurl -d {} /app/service-key.json gs://esper/{} ' \
                    .format(duration, self.path)
        url = sp.check_output(
            fetch_cmd,
            shell=True).decode('utf-8').split('\n')[1].split('\t')[-1]
        return url


class Tag(EsperModel):
    name = CharField()


class VideoTag(EsperModel):
    video = FK(Video)
    tag = FK(Tag)


class Frame(Frame):
    tags = models.ManyToManyField(Tag)
    shot_boundary = models.BooleanField()


class Labeler(EsperModel):
    name = CharField()
    data_path = CharField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)


class Labeled(EsperModel):
    labeler = FK(Labeler)

    class Meta(EsperModel.Meta):
        abstract = True


class Gender(EsperModel):
    name = CharField()


Track = Track(Labeler)


class Commercial(Track):
    pass


class Topic(EsperModel):
    name = CharField(unique=True)


class Segment(Track):
    topics = models.ManyToManyField(Topic)
    polarity = models.FloatField(null=True)
    subjectivity = models.FloatField(null=True)


class Shot(Track):
    in_commercial = models.BooleanField(default=False)


class Pose(Labeled, Pose, EsperModel):
    frame = FK(Frame)


class Face(Labeled, BoundingBox, EsperModel):
    frame = FK(Frame)
    shot = FK(Shot, null=True)
    background = models.BooleanField(default=False)
    is_host = models.BooleanField(default=False)
    blurriness = models.FloatField(null=True)
    probability = models.FloatField(default=1.)

    class Meta(EsperModel.Meta):
        unique_together = ('labeler', 'frame', 'bbox_x1', 'bbox_x2', 'bbox_y1',
                           'bbox_y2')


class FaceTag(EsperModel):
    face = FK(Face)
    score = models.FloatField(default=1.)
    tag = FK(Tag)
    labeler = FK(Labeler)

    class Meta(EsperModel.Meta):
        unique_together = ('labeler', 'face')


class FaceGender(Labeled, EsperModel):
    face = FK(Face)
    gender = FK(Gender)
    probability = models.FloatField(default=1.)

    class Meta(EsperModel.Meta):
        unique_together = ('labeler', 'face')


class FaceIdentity(Labeled, EsperModel):
    face = FK(Face)
    identity = FK(Identity)
    probability = models.FloatField(default=1.)

    class Meta(EsperModel.Meta):
        unique_together = ('labeler', 'face')


class FaceFeatures(Labeled, Features, EsperModel):
    face = FK(Face)

    class Meta(EsperModel.Meta):
        unique_together = ('labeler', 'face')


class ScannerJob(EsperModel):
    name = CharField()


class Object(BoundingBox, EsperModel):
    frame = FK(Frame)
    label = models.IntegerField()
    probability = models.FloatField()


class LabeledCommercial(EsperModel):
    video = FK(Video)
    start = models.FloatField()
    end = models.FloatField()


class LabeledPanel(EsperModel):
    video = FK(Video)
    start = models.FloatField()
    end = models.FloatField()
    num_panelists = models.IntegerField()


class LabeledInterview(EsperModel):
    video = FK(Video)
    start = models.FloatField()
    end = models.FloatField()
    interviewer1 = CharField(default=None, blank=True, null=True)
    interviewer2 = CharField(default=None, blank=True, null=True)
    guest1 = CharField(default=None, blank=True, null=True)
    guest2 = CharField(default=None, blank=True, null=True)
    original = models.BooleanField(default=True)
    scattered_clips = models.BooleanField(default=False)


class HairColorName(EsperModel):
    name = CharField(unique=True)


class HairColor(Labeled, EsperModel):
    face = FK(Face)
    color = FK(HairColorName)

    class Meta(EsperModel.Meta):
        unique_together = ('labeler', 'face')


class ClothingName(EsperModel):
    name = CharField(unique=True)


class Clothing(Labeled, EsperModel):
    face = FK(Face)
    clothing = FK(ClothingName)

    class Meta(EsperModel.Meta):
        unique_together = ('labeler', 'face')


class HairLengthName(EsperModel):
    name = CharField(unique=True)


class HairLength(Labeled, EsperModel):
    face = FK(Face)
    length = FK(HairLengthName)

    class Meta(EsperModel.Meta):
        unique_together = ('labeler', 'face')
